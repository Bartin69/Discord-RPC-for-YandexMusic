import pystray
from PIL import Image

def create_tray_icon(presence):
    """Создание иконки в трее."""
    icon_image = Image.open("assets/icon.ico")

    def toggle_rpc(icon, item):
        """Включение/отключение RPC."""
        presence.enabled = not presence.enabled
        icon.update_menu()

    def exit_app(icon, item):
        """Выход из приложения."""
        icon.stop()
        presence.running = False
        if presence.rpc:
            presence.rpc.close()
        exit()

    # Меню для иконки в трее
    menu = (
        pystray.MenuItem("Включить/Отключить RPC", toggle_rpc, checked=lambda item: presence.enabled),
        pystray.MenuItem("Выход", exit_app),
    )

    # Создаем иконку в трее
    icon = pystray.Icon("YandexMusicRPC", icon_image, "Yandex Music RPC", menu)
    icon.run()