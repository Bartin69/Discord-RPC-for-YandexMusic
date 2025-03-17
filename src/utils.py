import psutil

def is_discord_running():
    """
    Проверяет, запущен ли Discord.

    :return: True, если Discord запущен, иначе False.
    """
    try:
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == 'Discord.exe':
                return True
        return False
    except Exception as e:
        print(f"[WinYandexMusicRPC] -> Error checking Discord: {e}")
        return False

def format_time(current_time, total_time):
    """
    Форматирует время в виде "02:47 ______ 03:05".

    :param current_time: Текущее время в секундах.
    :param total_time: Общее время трека в секундах.
    :return: Строка с отформатированным временем.
    """
    def to_min_sec(seconds):
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"

    current_str = to_min_sec(current_time)
    total_str = to_min_sec(total_time)
    progress = int((current_time / total_time) * 10)  # 10 символов для прогресса
    progress_bar = "▬" * progress + " " * (10 - progress)  # Используем символы Unicode для прогресса
    return f"{current_str} {progress_bar} {total_str}"