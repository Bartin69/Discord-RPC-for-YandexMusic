import os
import subprocess
import sys

def install_dependencies():
    """Устанавливает необходимые зависимости, если они не установлены."""
    required_libraries = [
        "pypresence",
        "yandex-music",
        "psutil",
        "pystray",
        "pillow",
        "winsdk",
        "pyinstaller",
    ]

    print("Проверка и установка зависимостей...")
    for lib in required_libraries:
        try:
            # Проверяем, установлена ли библиотека
            __import__(lib)
            print(f"{lib} уже установлена.")
        except ImportError:
            # Если библиотека не установлена, устанавливаем её
            print(f"Установка {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

def build_exe():
    """Создает .exe-файл с помощью PyInstaller."""
    # Устанавливаем зависимости, если они не установлены
    install_dependencies()

    # Путь к иконке
    icon_path = os.path.join("assets", "icon.ico")

    # Команда для сборки .exe
    command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        f"--icon={icon_path}",
        "src/main.py"
    ]

    # Запуск команды
    print("Сборка .exe...")
    subprocess.run(command)

    print("\nСборка завершена. Исполняемый файл находится в папке 'dist'.")

if __name__ == "__main__":
    build_exe()