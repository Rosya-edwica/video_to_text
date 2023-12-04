import os
import logging
from time import perf_counter
import argparse

import audio
import video
import gpt

VIDEOS_DIR = "data/videos/"
GPT_QUERY = "Ты профессионал в обработке большого текста. Мне нужно проверить своих студентов на знание текста.\nСоставь тест из 10 вопросов. Важно, чтобы вопросы были сложными и не содержали в себе подсказок. Ответы должны отличаться друг от друга (нельзя допустить, чтобы ответ всегда был в пункте a) например. Текст из которого нужно брать ответы на эти вопросы:\n"


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-m", "--method", required=True, help="""
    Выберите метод для транскрибации видео:,
    1. whisher - транскрибация с помощью openai,
    2. google - транскрибация с помощью google_recognize (бесплатный, но не качественный результат)""")
args = arg_parser.parse_args()

logging.basicConfig(filename="logs.log", filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S', level=logging.DEBUG)


def main():
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    if len(os.listdir(VIDEOS_DIR)) == 0:
        exit(f"Добавьте хотя бы одно видео формата .mp4 в папку: {VIDEOS_DIR}")

    transcriber = audio.Transcriber()
    for file in os.listdir(VIDEOS_DIR):
        start_time = perf_counter()
        video_file = os.path.join(VIDEOS_DIR, file)
        audio_file = video.video_to_audio(video_file, audio_format="mp3")

        transcriber.set_new_audio_path(audio_file)
        text = transcriber.transcribe(min_per_split=1, method=args.method)
        answer = gpt.create_test_by_text(GPT_QUERY, text)
        if answer:
            logging.info(msg=f"Время на один файл: {perf_counter() - start_time}\tСтоимость запроса:{answer.Cost.Dollar}\tКоличество токенов:{answer.AnswerTokens + answer.QuestionTokens}")
            logging.info(msg=f"Тест по тексту: {answer.Text}")
            gpt.save_answer(answer, file.replace(".mp4", ".txt"))
        

if __name__ == "__main__":
    main()