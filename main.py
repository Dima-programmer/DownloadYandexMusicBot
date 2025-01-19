import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from aiogram.types import FSInputFile
from dotenv import load_dotenv
from dw_yandex_music import Client
from yandex_music import Track

# Загрузка переменных окружения из .env файла
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
YANDEX_TOKEN = os.getenv('YANDEX_MUSIC_TOKEN')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()  # Создаем диспетчер без передачи бота

# Инициализация клиента Yandex Music
try:
    ya_music_client = Client(YANDEX_TOKEN)
except Exception as e:
    logging.error(f"Ошибка инициализации клиента Yandex Music: {e}")
    raise


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    me = await bot.get_me()
    try:
        await message.answer(
            f"Привет! Используй @{me.username} <название трека> для поиска музыки или отправь мне URL трека Яндекс.Музыка для скачивания.")
    except Exception as ex_:
        logging.error(f'Ошибка при /start - {ex_}')


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    try:
        await message.answer(
            "Используй /start для начала. Отправь URL трека для скачивания или используй @<bot_name> <название трека> для поиска.")
    except Exception as ex_:
        logging.error(f'Ошибка при /help - {ex_}')


@dp.message(F.text.startswith('http'))
async def download_track(message: types.Message):
    url = message.text
    try:
        file_path = ya_music_client.download(url)  # Получаем путь к скачанному файлу
        if file_path:
            msg = await message.answer("Трек успешно скачан! Отправляю файл...")

            # Используем InputFile с указанием пути к файлу
            audio = FSInputFile(file_path)  # Убедитесь, что передаете путь к файлу

            await bot.send_audio(message.chat.id, audio)
            os.remove(file_path)  # Удаляем файл после отправки
            await msg.delete()
        else:
            await message.answer("Не удалось скачать трек. Проверьте URL.")
    except Exception as e:
        logging.error(f"Ошибка при скачивании трека: {e}")
        try:
            await message.answer("Произошла ошибка при скачивании трека. Проверьте URL и попробуйте снова.")
        except Exception as ex_:
            pass


@dp.inline_query()
async def inline_search(inline_query: types.InlineQuery):
    query = inline_query.query.strip()
    if not query:
        await inline_query.answer([])
        return

    try:
        # Выполняем поиск треков по названию
        tracks: dict[str:list[Track]] = ya_music_client._client.search(query)['tracks']  # Убираем аргумент type

        if not tracks:
            await inline_query.answer([], switch_pm_text="Треки не найдены.", switch_pm_parameter="help")
            return

        results = []
        for track in tracks['results']:
            track_url = ya_music_client.get_url_from_track(track)
            results.append(types.InlineQueryResultArticle(
                id=str(track.id),
                title=track.title,
                input_message_content=types.InputTextMessageContent(
                    message_text=track_url
                ),
                description=', '.join(track.artists_name()),
                thumb_url=track.get_cover_url() or None
            ))

        await inline_query.answer(results)
    except Exception as e:
        logging.error(f"Ошибка при выполнении поиска: {e}")
        try:
            await inline_query.answer([], switch_pm_text="Произошла ошибка при поиске треков.",
                                      switch_pm_parameter="help")
        except Exception as ex_:
            pass


async def main():
    # Запуск бота
    try:
        await dp.start_polling(bot)  # Передаем экземпляр бота в run_polling
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
