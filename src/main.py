import os
import logging
from time import perf_counter
import argparse
import json
from datetime import datetime
import tools
import core
from db import Mongo
from rich.progress import track


VIDEOS_DIR = "data/videos/"
GPT_QUERY = "Ты профессионал в обработке большого текста. Мне нужно проверить своих студентов на знание текста.\nСоставь тест из 10 вопросов. Важно, чтобы вопросы были сложными и не содержали в себе подсказок. Ответы должны отличаться друг от друга (нельзя допустить, чтобы ответ всегда был в пункте a) например. Структура твоего ответа: '1. Вопрос\na) первый вариант\nb) второй вариант\nc) третий вариант\nd) четвертый вариант\nОтвет: полный вариант'. Текст из которого нужно брать ответы на эти вопросы:\n"


def main():
    """Отправная точка приложения:
    1. Выбираем способ работы приложения с помощью аргументов командной строки
    2. В зависимости от способа запускаем обработку видео
    3. Качаем видео-файл по ссылке из файла videos.csv
    4. Достаем из видео аудио-дорожку
    5. Удаляем видео
    6. Дробим аудио-дорожку на минутные голосовые сообщения
    7. Достаем из голосового сообщения текст
    8. Собираем текст из всех голосовых сообщений воедино.
    9. Генерим тест по тексту.
    """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-m", "--method", required=True, help="""
        Выберите метод для транскрибации аудио:,
        1. whisper - транскрибация с помощью openai,
        2. google - транскрибация с помощью google_recognize (бесплатный, но не качественный результат)""")
    arg_parser.add_argument("-s", "--source", required=True, help="""
        Выберите метод для загрузки видео:,
        1. file - загрузка файлов из папки /data/videos/ (.mp4 формат),
        2. url - загрузка файлов из файла /data/videos/videos.csv, в будет таблица с такими колонками(название видео, ссылка для скачивания, ссылка на видео)""")
    args = arg_parser.parse_args()

    logging.basicConfig(filename="logs.log", filemode='w', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S', level=logging.DEBUG)
    logging.getLogger("pydub").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


    if args.method not in ("whisper", "google"):
        exit("Неправильный аргумент")

    match args.source:
        case "file":
            generate_tests_to_videos_by_files(args.method)
        case "url":
            generate_tests_to_videos_by_urls(args.method)


@tools.stopwatch_decorator
def generate_tests_to_videos_by_urls(transcribation_method: str):
    videos = tools.get_videos_from_csv(os.path.join(VIDEOS_DIR, "videos.csv"))
    for item in track(range(len(videos)), description="Обработка видео по ссылкам для скачивания..."):
        video = videos[item]
        video_path = os.path.join(VIDEOS_DIR, video.Name+".mp4")
        try:
            tools.download_video(video.DownloadUrl, video_path)
            generate_test_by_video_file(video_path, transcribation_method)
        except BaseException as err:
            print(f"Не удалось обработать видео: {video_path}: {err}")

@tools.stopwatch_decorator
def generate_tests_to_videos_by_files(transcribation_method: str):
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    if len(os.listdir(VIDEOS_DIR)) == 0:
        logging.error(f"Добавьте хотя бы одно видео формата .mp4 в папку: {VIDEOS_DIR}")
        exit(f"Добавьте хотя бы одно видео формата .mp4 в папку: {VIDEOS_DIR}")

    files = os.listdir(VIDEOS_DIR)
    for item in track(range(len(files)), description="Обработка видео по файлам..."):
        file = files[item]
        video_path = os.path.join(VIDEOS_DIR, file)
        generate_test_by_video_file(video_path, transcribation_method)


@tools.stopwatch_decorator
def generate_test_by_video_file(videofile_path: str, transcribation_method: str):
    if not videofile_path.endswith(".mp4"):
        logging.error(f"Файл '{videofile_path}' не подходит, нужно расширение .mp4!")
        return
    start_time = perf_counter()
    video_name = videofile_path.replace(".mp4", "")
    # audio_file = core.video.video_to_audio(videofile_path, audio_format="mp3")
    # transcriber.set_new_audio_path(audio_file)
    # text = transcriber.transcribe(min_per_split=1, method=transcribation_method, summarize_text=True)

    chunks = core.video.video_to_chunks(videofile_path)
    text = transcriber.transcribe_by_chunks(chunks)
    mongo.save_transcribation(video_name, text)
    answer = core.gpt.create_test_by_text(GPT_QUERY, text)
    if not answer:
        return

    mongo.save_gpt_responce(video_name, answer)
    test = tools.parse_test(answer.Text)
    mongo.save_test(video_name, test)
    kafka_message = {
        "date": str(datetime.now()),
        "promt": GPT_QUERY + text,
        "answer": answer.Text,
        "cost_usd": answer.Cost.Dollar,
        "tokens": answer.AnswerTokens + answer.QuestionTokens,
        "time_exe": perf_counter() - start_time
    }
    producer.send_to_text_partition(json.dumps(kafka_message))


if __name__ == "__main__":
    mongo = Mongo()
    producer = tools.NewProducer()
    transcriber = core.audio.Transcriber()
    main()
    # create_chunks_for_all_audio_files()
    # create_test_by_chunks()
    mongo.download_all()