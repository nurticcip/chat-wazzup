import subprocess
import sys

def run_command(command):
    """Выполнение команды с выводом результата"""
    print(f"Выполняется: {command}")
    try:
        process = subprocess.run(
            command, 
            shell=True, 
            text=True, 
            capture_output=True, 
            check=True
        )
        if process.stdout:
            print(process.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка: {e}")
        print(f"Детали: {e.stderr}")
        return False

def main():
    # Проверка наличия аргумента с сообщением коммита
    if len(sys.argv) < 2:
        print("Ошибка: Не указано сообщение коммита")
        print("Использование: python git_push_script.py \"Сообщение коммита\"")
        sys.exit(1)

    # Получаем сообщение коммита из первого аргумента
    commit_message = sys.argv[1]

    # Последовательно выполняем git команды
    commands = [
        "git add .",
        f'git commit -m "{commit_message}"',
        "git push"
    ]

    # Выполняем команды одна за другой
    for cmd in commands:
        if not run_command(cmd):
            print("Процесс остановлен из-за ошибки.")
            sys.exit(1)

    print("✅ Все команды успешно выполнены!")

if __name__ == "__main__":
    main()