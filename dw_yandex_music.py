# dw_yandex_music.py

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
            with open(f"{track.title}.mp3", "wb") as f:
                f.write(track_source)
            print(f"Трек '{track.title}' успешно скачан.")
            return f"{track.title}.mp3"
        except Exception as ex:
            # print(f"Ошибка при скачивании трека: {ex}")
            return
