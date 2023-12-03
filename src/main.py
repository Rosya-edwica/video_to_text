import os
import logging
from time import perf_counter

import audio
import video
import gpt

VIDEOS_DIR = "data/videos/"

logging.basicConfig(filename="logs.log", filemode='a', format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S', level=logging.DEBUG)

def main():
    if len(os.listdir(VIDEOS_DIR)) == 0:
        exit(f"Добавьте хотя бы одно видео формата .mp4 в папку: {VIDEOS_DIR}")

    for file in os.listdir(VIDEOS_DIR):
        start_time = perf_counter()
        video_file = os.path.join(VIDEOS_DIR, file)
        audio_file = video.video_to_audio(video_file)

        text = audio.transcribe_large_audio(audio_file)
        answer = gpt.get_test_for_text(text)
        if not answer:
            continue
        logging.info(msg=f"Время на один файл: {perf_counter() - start_time}\tСтоимость запроса:{answer.Cost.Dollar}\tКоличество токенов:{answer.AnswerTokens + answer.QuestionTokens}")
        logging.info(msg=f"Тест по тексту: {answer.Text}")


if __name__ == "__main__":
    main()
