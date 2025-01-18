import asyncio
import time
from enum import Enum
from itertools import permutations
from yandex_music import Client
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
import pypresence
from .utils import format_time, is_discord_running

# Идентификатор клиента Discord для Rich Presence
client_id = '1191876731808784525'

# Флаг для поиска трека с 100% совпадением названия и автора. Иначе будет найден близкий результат.
strong_find = True

# Переменная для хранения предыдущего трека и избежания дублирования обновлений.
name_prev = str()

# Enum для статуса воспроизведения мультимедийного контента.
class PlaybackStatus(Enum):
    """Статусы воспроизведения мультимедиа."""
    Unknown = 0
    Opened = 2
    Paused = 3
    Playing = 4
    Stopped = 5

async def get_media_info():
    """
    Получает информацию о текущем медиа-контенте через Windows SDK.

    :return: Словарь с информацией о треке или None, если информация недоступна.
    """
    try:
        sessions = await MediaManager.request_async()
        current_session = sessions.get_current_session()
        if current_session:
            info = await current_session.try_get_media_properties_async()
            info_dict = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != '_'}
            info_dict['genres'] = list(info_dict['genres'])
            playback_status = PlaybackStatus(current_session.get_playback_info().playback_status)
            info_dict['playback_status'] = playback_status.name
            return info_dict
        raise Exception('The music is not playing right now.')
    except Exception as e:
        print(f"[WinYandexMusicRPC] -> Error getting media info: {e}")
        return None

class Presence:
    """Класс для управления Discord Rich Presence."""
    def __init__(self) -> None:
        self.client = None
        self.currentTrack = None
        self.rpc = None
        self.running = False
        self.paused = False
        self.start_time = None
        self.enabled = True
        self.track_start_time = None

    def start(self) -> None:
        """Запуск Rich Presence."""
        if not is_discord_running():
            print("[WinYandexMusicRPC] -> Discord is not launched")
            return

        # Создаем новый цикл событий для этого потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.rpc = pypresence.Presence(client_id, loop=loop)
        self.rpc.connect()
        self.client = Client().init()
        self.running = True
        self.currentTrack = None

        while self.running:
            if not self.enabled:
                self.rpc.clear()
                time.sleep(1)
                continue

            currentTime = time.time()

            if not is_discord_running():
                print("[WinYandexMusicRPC] -> Discord was closed")
                self.running = False
                return

            ongoing_track = self._get_track()

            # Проверяем, что ongoing_track не None
            if ongoing_track is None:
                print("[WinYandexMusicRPC] -> Failed to get track information")
                time.sleep(1)
                continue

            if self.currentTrack != ongoing_track:
                self._update_track(ongoing_track, currentTime)
            else:
                self._update_time(ongoing_track, currentTime)

            time.sleep(1)

    def _update_track(self, track, current_time):
        """Обновление информации о треке."""
        if track['success']:
            self.track_start_time = current_time - track['current_position'] if track['current_position'] else current_time
            self.start_time = self.track_start_time

            elapsed_time = current_time - self.start_time
            time_str = format_time(elapsed_time, track['durationSec'])

            try:
                self.rpc.update(
                    details=track['label'],
                    state=time_str,
                    large_image=track['og-image'],
                    large_text=track['album'],
                    small_image="play" if track["playback"] == PlaybackStatus.Playing.name else "pause",
                    small_text="Playing" if track["playback"] == PlaybackStatus.Playing.name else "Paused",
                    buttons=[{"label": "Listen on Yandex Music", "url": track['link']}]
                )
            except Exception as e:
                print(f"[WinYandexMusicRPC] -> Error updating RPC: {e}")
        else:
            self.rpc.clear()
            print(f"[WinYandexMusicRPC] -> Clear RPC")

        self.currentTrack = track

    def _update_time(self, track, current_time):
        """Обновление времени трека."""
        if track['success']:
            elapsed_time = current_time - self.start_time
            time_str = format_time(elapsed_time, track['durationSec'])

            if track["playback"] != PlaybackStatus.Playing.name and not self.paused:
                self.paused = True
                print(f"[WinYandexMusicRPC] -> Track {track['label']} on pause")
                self._update_paused_track(track, time_str)
            elif track["playback"] == PlaybackStatus.Playing.name and self.paused:
                print(f"[WinYandexMusicRPC] -> Track {track['label']} off pause.")
                self.paused = False

            try:
                self.rpc.update(
                    details=track['label'],
                    state=time_str,
                    large_image=track['og-image'],
                    large_text=track['album'],
                    small_image="play" if track["playback"] == PlaybackStatus.Playing.name else "pause",
                    small_text="Playing" if track["playback"] == PlaybackStatus.Playing.name else "Paused",
                    buttons=[{"label": "Listen on Yandex Music", "url": track['link']}]
                )
            except Exception as e:
                print(f"[WinYandexMusicRPC] -> Error updating RPC: {e}")

    def _update_paused_track(self, track, time_str):
        """Обновление статуса при паузе."""
        try:
            self.rpc.update(
                details=track['label'],
                state=f"Paused | {time_str}",
                large_image=track['og-image'],
                large_text=track['album'],
                small_image="pause",
                small_text="Paused",
                buttons=[{"label": "Listen on Yandex Music", "url": track['link']}]
            )
        except Exception as e:
            print(f"[WinYandexMusicRPC] -> Error updating RPC: {e}")

    def _get_track(self) -> dict:
        """Получение информации о текущем треке."""
        try:
            current_media_info = asyncio.run(get_media_info())
            if not current_media_info:
                print("[WinYandexMusicRPC] -> No media info available")
                return {'success': False}

            name_current = current_media_info["artist"] + " - " + current_media_info["title"]
            global name_prev
            global strong_find
            if str(name_current) != name_prev:
                print("[WinYandexMusicRPC] -> Now listen: " + name_current)
            else:  # Если песня уже играет, то не нужно ее искать повторно. Просто вернем её с актуальным статусом паузы.
                currentTrack_copy = self.currentTrack.copy()
                currentTrack_copy["playback"] = current_media_info['playback_status']
                return currentTrack_copy

            name_prev = str(name_current)
            search = self.client.search(name_current, True, "all", 0, False)

            if not search.best or not hasattr(search.best, 'result'):
                print(f"[WinYandexMusicRPC] -> Can't find the song: {name_current}")
                return {'success': False}
            if search.best.type not in ['music', 'track', 'podcast_episode']:
                print(f"[WinYandexMusicRPC] -> Can't find the song: {name_current}, the best result has the wrong type")
                return {'success': False}
            findTrackName = ', '.join([str(elem) for elem in search.best.result.artists_name()]) + " - " + \
                            search.best.result.title

            # Авторы могут отличатся положением, поэтому делаем все возможные варианты их порядка.
            artists = search.best.result.artists_name()
            all_variants = list(permutations(artists))
            all_variants = [list(variant) for variant in all_variants]
            findTrackNames = []
            for variant in all_variants:
                findTrackNames.append(', '.join([str(elem) for elem in variant]) + " - " + search.best.result.title)
            # Также может отличаться регистр, так что приведём всё в один регистр.
            boolNameCorrect = any(name_current.lower() == element.lower() for element in findTrackNames)

            if strong_find and not boolNameCorrect:
                print(f"[WinYandexMusicRPC] -> Cant find the song (strong_find). Now play: {name_current}. But we find: {findTrackName}")
                return {'success': False}

            track = search.best.result
            trackId = track.trackId.split(":")

            if track:
                return {
                    'success': True,
                    'label': f"{', '.join(track.artists_name())} - {track.title}",
                    'duration': "Duration: None",
                    'link': f"https://music.yandex.ru/album/{trackId[1]}/track/{trackId[0]}/",
                    'durationSec': track.duration_ms // 1000,
                    'playback': current_media_info['playback_status'],
                    'og-image': "https://" + track.og_image[:-2] + "400x400",
                    'album': track.albums[0].title if track.albums else "Unknown Album",  # Название альбома
                    'current_position': 0  # Добавляем ключ current_position
                }

        except Exception as exception:
            print(f"[WinYandexMusicRPC] -> Something happened: {exception}")
            return {'success': False}