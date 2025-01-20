# dw_yandex_music.py
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1
from yandex_music import Client as YandexClient


class Client:
    def __init__(self, token):
        """Инициализация клиента Yandex Music с токеном."""
        self._client = YandexClient(token)

    def download(self, url):
        """Скачивание трека по указанному URL."""
        return self._download_track(url)

    def get_url_from_track(self, track):
        return f"https://music.yandex.ru/track/{track.id}"

    def _download_track(self, url):
        """Внутренний метод для скачивания трека."""
        url = url.split('?')[0]
        print(url)
        track_id = self._extract_track_id(url)
        if not track_id:
            # print("Неверный URL трека.")
            return

        try:
            track = self._client.tracks(track_id)[0]
        except Exception as ex:
            # print(f"Ошибка при получении трека: {ex}")
            return

        if self._is_valid_url(url, track):
            return self._save_track(track)
        else:
            # print("Ссылка на трек не совпадает с введенной.")
            return

    @staticmethod
    def _extract_track_id(url):
        """Извлечение ID трека из URL."""
        try:
            return url.split("/")[-1]
        except IndexError:
            return None

    def _is_valid_url(self, url, track):
        """Проверка, совпадает ли URL с формируемыми ссылками на трек."""
        track_id = track.id
        links_for_track = {
            f"https://music.yandex.ru/track/{track_id}",
        }

        if track.albums:
            for album in track.albums:
                links_for_track.add(
                    f"https://music.yandex.ru/album/{album.id}/track/{track_id}")

        return url in links_for_track

    def _save_track(self, track):
        """Сохранение трека в файл."""
        try:
            track_source = track.download_bytes()
            file_name = f"{track.title}.mp3"
            with open(file_name, "wb") as f:
                f.write(track_source)
            try:
                audio = MP3(file_name, ID3=ID3)
            except ID3NoHeaderError:
                audio = MP3(file_name)
                audio.add_tags()

            # Устанавливаем метаданные
            audio.tags.add(TIT2(encoding=3, text=track.title))
            audio.tags.add(TPE1(encoding=3, text=', '.join(track.artists_name())))

            print(f"Трек '{track.title}' успешно скачан.")
            return f"{track.title}.mp3"
        except Exception as ex:
            # print(f"Ошибка при скачивании трека: {ex}")
            return
