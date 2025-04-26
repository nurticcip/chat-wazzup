from flask import Blueprint, jsonify, session, send_file, request, current_app
import sqlite3
from io import BytesIO
import bcrypt
import os
from werkzeug.utils import secure_filename
import mimetypes
from datetime import datetime

user_bp = Blueprint('user', __name__)

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_user_photo(user_id=None):
    """Get user profile photo"""
    if user_id is None and 'user_id' in session:
        user_id = session['user_id']
    elif user_id is None:
        return None
    
    conn = get_db_connection()
    try:
        result = conn.execute('SELECT profile_photo FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        
        if not result or not result['profile_photo']:
            return None
        
        return BytesIO(result['profile_photo'])
    except Exception as e:
        if conn:
            conn.close()
        print(f"Error getting user photo: {e}")
        return None

@user_bp.route('/api/user/photo', methods=['GET'])
def get_user_photo_route():
    """Get user profile photo"""
    if 'user_id' not in session:
        return send_file('static/images/avatar.png', mimetype='image/png')
    
    user_id = session['user_id']
    photo = get_user_photo(user_id)
    
    if not photo:
        return send_file('static/images/avatar.png', mimetype='image/png')
    
    return send_file(photo, mimetype='image/jpeg')

@user_bp.route('/api/user/photo', methods=['POST'])
def upload_user_photo():
    """Upload user profile photo"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Пользователь не авторизован'}), 401
    
    if 'profile_photo' not in request.files:
        return jsonify({'success': False, 'message': 'Файл не найден'}), 400
    
    photo_file = request.files['profile_photo']
    
    if not photo_file.filename:
        return jsonify({'success': False, 'message': 'Файл не выбран'}), 400
    
    # Считываем данные фотографии
    photo_data = photo_file.read()
    
    # Сохраняем фотографию в базе данных
    conn = get_db_connection()
    conn.execute('UPDATE users SET profile_photo = ? WHERE id = ?', 
                (photo_data, session['user_id']))
    conn.commit()
    conn.close()
    
    # Возвращаем timestamp для предотвращения кеширования
    timestamp = int(datetime.now().timestamp())
    return jsonify({
        'success': True, 
        'message': 'Фото профиля обновлено',
        'timestamp': timestamp
    })

@user_bp.route('/api/user/update-photo', methods=['POST'])
def update_user_photo():
    """Alternative endpoint for profile photo update"""
    # Перенаправляем на основной endpoint для совместимости
    return upload_user_photo()

@user_bp.route('/api/users/<int:user_id>/photo', methods=['GET'])
def get_other_user_photo(user_id):
    """Get other user's profile photo"""
    photo = get_user_photo(user_id)
    
    if not photo:
        return send_file('static/images/avatar.png', mimetype='image/png')
    
    return send_file(photo, mimetype='image/jpeg')

@user_bp.route('/api/user', methods=['GET'])
def get_user_info():
    """Get current user info"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Пользователь не авторизован'}), 401
    
    user_id = session['user_id']
    
    conn = get_db_connection()
    user = conn.execute('SELECT id, nickname, email FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404
    
    email = user['email'] if 'email' in user.keys() else ""
    
    return jsonify({
        'success': True, 
        'user': {
            'id': user['id'],
            'nickname': user['nickname'],
            'email': email
        }
    })

@user_bp.route('/api/users/search', methods=['GET'])
def search_users():
    """Поиск пользователей по никнейму"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Не авторизован'}), 401
    
    query = request.args.get('q', '')
    if not query:
        return jsonify({'success': False, 'message': 'Не указан запрос поиска'}), 400
    
    current_user_id = session['user_id']
    
    conn = get_db_connection()
    users = conn.execute('''
        SELECT id, nickname
        FROM users
        WHERE id != ? AND nickname LIKE ?
        ORDER BY nickname
        LIMIT 20
    ''', (current_user_id, f'%{query}%')).fetchall()
    
    result = []
    for user in users:
        # Для каждого пользователя проверяем наличие фото
        has_photo = get_user_photo(user['id']) is not None
        photo_url = f'/api/users/{user["id"]}/photo' if has_photo else None
        
        result.append({
            'id': user['id'],
            'nickname': user['nickname'],
            'photo': photo_url
        })
    
    conn.close()
    
    return jsonify({'success': True, 'users': result})

@user_bp.route('/api/user/update-password', methods=['POST'])
def update_password():
    """Обновляет пароль пользователя"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Не авторизован'}), 401
    
    data = request.get_json()
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({'success': False, 'message': 'Неверные параметры запроса'}), 400
    
    current_password = data['current_password']
    new_password = data['new_password']
    
    # Проверка длины нового пароля
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Пароль должен содержать не менее 6 символов'}), 400
    
    conn = get_db_connection()
    user = conn.execute('SELECT password FROM users WHERE id = ?', 
                      (session['user_id'],)).fetchone()
    
    if not user:
        conn.close()
        return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404
    
    # Проверяем текущий пароль
    if not bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
        conn.close()
        return jsonify({'success': False, 'message': 'Неверный текущий пароль'}), 401
    
    # Хешируем новый пароль
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Обновляем пароль
    conn.execute('UPDATE users SET password = ? WHERE id = ?', 
                (hashed_password, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Пароль успешно обновлен'})

@user_bp.route('/api/users/current', methods=['GET'])
def get_current_user():
    """Получает информацию о текущем авторизованном пользователе"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Не авторизован'}), 401
    
    conn = get_db_connection()
    user = conn.execute('SELECT id, nickname FROM users WHERE id = ?', 
                      (session['user_id'],)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'success': False, 'message': 'Пользователь не найден'}), 404
    
    # Проверка наличия фото
    has_photo = get_user_photo(user['id']) is not None
    photo_url = f'/api/user/photo' if has_photo else None
    
    return jsonify({
        'success': True, 
        'user': {
            'id': user['id'], 
            'nickname': user['nickname'],
            'name': user['nickname'],  # Используем nickname как name для совместимости
            'photo': photo_url
        }
    })
