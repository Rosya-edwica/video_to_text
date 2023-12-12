import os
import logging
from time import perf_counter
import argparse
import json
from datetime import datetime

import audio
import video
import gpt
from kafka_test import NewProducer

VIDEOS_DIR = "data/videos/"
GPT_QUERY = "Ты профессионал в обработке большого текста. Мне нужно проверить своих студентов на знание текста.\nСоставь тест из 10 вопросов. Важно, чтобы вопросы были сложными и не содержали в себе подсказок. Ответы должны отличаться друг от друга (нельзя допустить, чтобы ответ всегда был в пункте a) например. Структура твоего ответа: '1. Вопрос\na) первый вариант\nb) второй вариант\nc) третий вариант\nd) четвертый вариант\nОтвет: полный вариант'. Текст из которого нужно брать ответы на эти вопросы:\n"


arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("-m", "--method", required=True, help="""
    Выберите метод для транскрибации видео:,
    1. whisper - транскрибация с помощью openai,
    2. google - транскрибация с помощью google_recognize (бесплатный, но не качественный результат)""")
args = arg_parser.parse_args()

logging.basicConfig(filename="logs.log", filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S', level=logging.DEBUG)

if args.method not in ("whisper", "google"):
    exit("Неправильный аргумент")

def main():
    print("Selected method:", args.method)
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    if len(os.listdir(VIDEOS_DIR)) == 0:
        exit(f"Добавьте хотя бы одно видео формата .mp4 в папку: {VIDEOS_DIR}")

    producer = NewProducer()
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
            gpt.save_answer(answer.Text, file.replace(".mp4", ".txt"))
            kafka_message = {
                "date": str(datetime.now()),
                "promt": GPT_QUERY + text,
                "answer": answer.Text,
                "cost_usd": answer.Cost.Dollar,
                "cost_rub": answer.Cost.Ruble,
                "tokens": answer.AnswerTokens + answer.QuestionTokens,
                "time_exe": perf_counter() - start_time
            }
            producer.send_to_text_partition(json.dumps(kafka_message))
        

if __name__ == "__main__":
    main()