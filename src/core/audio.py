import os
import math
import shutil
from typing import Literal

import speech_recognition as sr
from pydub import AudioSegment
import logging
from core import gpt
from gensim.summarization.summarizer import summarize


CHUNKS_DIR = "data/chunks/"
AUDIO_DIR = "data/audio/"


def clean_cache():
    shutil.rmtree(CHUNKS_DIR)
    shutil.rmtree(AUDIO_DIR)


class Transcriber:
    def __init__(self, audio_path: str = None):
        self.Recognizer = sr.Recognizer()
        self.audio_path = audio_path
        if self.audio_path:
            self.main_audio = AudioSegment.from_wav(self.audio_path)
        self.text = ""

    def set_new_audio_path(self, path: str):
        self.audio_path = path
        if self.audio_path.endswith(".wav"):
            self.main_audio = AudioSegment.from_wav(self.audio_path)
        elif self.audio_path.endswith(".mp3"):
            self.main_audio = AudioSegment.from_mp3(self.audio_path)

    def transcribe(self, min_per_split: int, method: list[Literal["whisper", "google"]], summarize_text: bool = False) -> str:
        """summarize - сокращать текст или нет"""
        if self.audio_path is None:
            exit("Забыли передать аудиофайл в class Transcribe")
        
        print(f"Извлекаем текст из аудио '{self.audio_path}'...")
        sound_mins = math.ceil(self.main_audio.duration_seconds / 60)
        os.makedirs(name=CHUNKS_DIR, exist_ok=True) 
        for i in range(0, sound_mins, min_per_split):
            chunk_filename = os.path.join(CHUNKS_DIR, f"chunk_{i}.wav")
            match method:
                case "whisper":
                    chunk_text = self.__get_text_for_chunk_by_whisper(chunk_filename, i, i+min_per_split)
                case "google":
                    chunk_text = self.__get_text_for_chunk_by_google(chunk_filename, i, i+min_per_split)
                case _:
                    return ""

            if chunk_text:
                self.text += chunk_text
        
        print(f"Извлекли текст. Количество слов: {len(self.text.split())}...")
        clean_cache()
        print(f"Стоимость обработки {self.audio_path} с помощью whisper составила:{sound_mins * gpt.GPT_MIN_PRICE}$ ({sound_mins} минут)")
        if summarize_text:
            percent = 0.7
            self.text = summarize(self.text, ratio=percent)
            print(f"Сократили текст c 100% до {percent * 100}% Количество слов: {len(self.text.split())}...")

        return self.text
    
    def __get_text_for_chunk_by_whisper(self, chunk_path: str, from_min: int, to_min: int):
        """Транскрибация текста с помощью OpenAI Whisper
        Данный подход выделяется высокой скоростью и качеством обработки.
        Но он требует подписку на OpenAI"""
        start = from_min * 60 * 1000
        end = to_min * 60 * 1000
        chunk_audio = self.main_audio[start:end]
        chunk_audio.export(chunk_path, format="mp3")
        text = gpt.transcribe_audio(chunk_path)
        return text

    def __get_text_for_chunk_by_google(self, chunk_path: str, from_min: int, to_min: int) -> str | None:
        """Транскрибация текста с помощью Google Recognizer
        Данный подход работает дольше и выдает текст не лучшего качества, но зато является бесплатным"""

        start = from_min * 60 * 1000
        end = to_min * 60 * 1000
        chunk_audio = self.main_audio[start:end]
        chunk_audio.export(chunk_path, format="wav")
        with sr.AudioFile(chunk_path) as source:
            audio_listened = self.Recognizer.record(source)
            try:
                text = self.Recognizer.recognize_google(audio_listened, language="ru-RU")
            except sr.UnknownValueError as err:
                logging.error(f"Ошибка при транскрибации аудио с помощью Google Recognizer: {err}")
                return None
            else:
                logging.info(f"Обработали кусок аудио: {chunk_path}")
                return text
