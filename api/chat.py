from flask import Blueprint, jsonify, request, session
import sqlite3
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@chat_bp.route('/api/messages', methods=['GET'])
def get_messages():
    """Get messages for a specific chat"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Пользователь не авторизован'}), 401
    
    chat_id = request.args.get('chat_id')
    if not chat_id:
        return jsonify({'success': False, 'message': 'Не указан ID чата'}), 400
    
    conn = get_db_connection()
    messages = conn.execute('''
        SELECT m.id, m.content, m.timestamp, m.sender_id, u.nickname as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.chat_id = ?
        ORDER BY m.timestamp ASC
    ''', (chat_id,)).fetchall()
    
    message_list = [{
        'id': message['id'],
        'content': message['content'],
        'timestamp': message['timestamp'],
        'sender_id': message['sender_id'],
        'sender_name': message['sender_name'],
        'is_own': message['sender_id'] == session['user_id']
    } for message in messages]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'messages': message_list
    })

@chat_bp.route('/api/messages', methods=['POST'])
def send_message():
    """Send a new message"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Пользователь не авторизован'}), 401
    
    data = request.get_json()
    if not data or 'chat_id' not in data or 'content' not in data:
        return jsonify({'success': False, 'message': 'Неполные данные'}), 400
    
    chat_id = data['chat_id']
    content = data['content']
    sender_id = session['user_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO messages (chat_id, sender_id, content) VALUES (?, ?, ?)',
        (chat_id, sender_id, content)
    )
    conn.commit()
    
    # Get the inserted message details
    message_id = cursor.lastrowid
    message = conn.execute('''
        SELECT m.id, m.content, m.timestamp, u.nickname as sender_name
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.id = ?
    ''', (message_id,)).fetchone()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'message': {
            'id': message['id'],
            'content': message['content'],
            'timestamp': message['timestamp'],
            'sender_id': sender_id,
            'sender_name': message['sender_name'],
            'is_own': True
        }
    })

@chat_bp.route('/api/chats', methods=['GET'])
def get_chats():
    """Get list of chats for current user"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Пользователь не авторизован'}), 401
    
    user_id = session['user_id']
    
    conn = get_db_connection()
    # Get direct chats
    direct_chats = conn.execute('''
        SELECT c.id, c.chat_type, 
               CASE 
                   WHEN u1.id = ? THEN u2.nickname
                   ELSE u1.nickname
               END as chat_name,
               CASE 
                   WHEN u1.id = ? THEN u2.id
                   ELSE u1.id
               END as other_user_id,
               c.created_at
        FROM chats c
        JOIN dialogs d ON c.id = d.chat_id
        JOIN users u1 ON d.user1_id = u1.id
        JOIN users u2 ON d.user2_id = u2.id
        WHERE d.user1_id = ? OR d.user2_id = ?
        ORDER BY c.created_at DESC
    ''', (user_id, user_id, user_id, user_id)).fetchall()
    
    # Convert to list of dicts
    chats_list = []
    for chat in direct_chats:
        # Get last message if exists
        last_message = conn.execute('''
            SELECT content, timestamp, sender_id
            FROM messages
            WHERE chat_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (chat['id'],)).fetchone()
        
        chat_dict = {
            'id': chat['id'],
            'type': chat['chat_type'],
            'name': chat['chat_name'],
            'other_user_id': chat['other_user_id'],
            'created_at': chat['created_at'],
            'last_message': {
                'content': last_message['content'] if last_message else None,
                'timestamp': last_message['timestamp'] if last_message else None,
                'is_own': last_message['sender_id'] == user_id if last_message else False
            } if last_message else None
        }
        chats_list.append(chat_dict)
    
    conn.close()
    
    return jsonify({'success': True, 'chats': chats_list})
