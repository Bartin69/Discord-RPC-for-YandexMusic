import threading
from src.presence import Presence
from src.tray_icon import create_tray_icon

def main():
    # Инициализация Presence
    presence = Presence()

    # Запуск RPC в отдельном потоке
    rpc_thread = threading.Thread(target=presence.start)
    rpc_thread.daemon = True
    rpc_thread.start()

    # Создание иконки в трее
    create_tray_icon(presence)

if __name__ == '__main__':
    main()