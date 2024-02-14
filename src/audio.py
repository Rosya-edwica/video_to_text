import os
import re
import math
import shutil
from typing import Literal

import speech_recognition as sr
from pydub import AudioSegment

import gpt

CHUNKS_DIR = "data/chunks/"
TEXT_DIR = "data/text/"


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

    def clean_cache(self):
        shutil.rmtree(CHUNKS_DIR)
    
    def transcribe(self, min_per_split: int, method: list[Literal["whisper", "google"]]) -> str:
        if self.audio_path is None:
            exit("Забыли передать аудиофайл в class Transcribe")
        
        sound_mins = math.ceil(self.main_audio.duration_seconds / 60)
        os.makedirs(name=CHUNKS_DIR, exist_ok=True) 
        for i in range(0, sound_mins, min_per_split):
            chunk_filename = os.path.join(CHUNKS_DIR, f"chunk_{i}.wav")
            match method:
                case "whisper":
                    chunk_text = self.__get_text_for_chunk_by_whisper(chunk_filename, i, i+min_per_split)
                case "google":
                    chunk_text = self.__get_text_for_chunk_by_google(chunk_filename, i, i+min_per_split)
            if chunk_text:
                self.text += chunk_text
        
        self.save_text()
        self.clean_cache()
        print(f"Стоимость обработки {self.audio_path} с помощью whisper составила:{sound_mins * gpt.GPT_MIN_PRICE}$ ({sound_mins} минут)")
        return self.text
    
    def __get_text_for_chunk_by_whisper(self, chunk_path: str, from_min: int, to_min: int):
        start = from_min * 60 * 1000
        end = to_min * 60 * 1000
        chunk_audio = self.main_audio[start:end]
        chunk_audio.export(chunk_path, format="mp3")
        text = gpt.transcribe_audio(chunk_path)
        print(chunk_path, ":", text)
        return text

    def __get_text_for_chunk_by_google(self, chunk_path: str, from_min: int, to_min: int) -> str | None:
        start = from_min * 60 * 1000
        end = to_min * 60 * 1000
        chunk_audio = self.main_audio[start:end]
        chunk_audio.export(chunk_path, format="wav")
        with sr.AudioFile(chunk_path) as source:
            audio_listened = self.Recognizer.record(source)
            try:
                text = self.Recognizer.recognize_google(audio_listened, language="ru-RU")
            except sr.UnknownValueError as e:
                print("Error:", str(e))
                return None
            else:
                print(chunk_path, ":", text)
                return text

    def save_text(self):
        os.makedirs(name=TEXT_DIR, exist_ok=True)
        audio_name = self.audio_path.split("/")[-1]
        text_path = os.path.join(TEXT_DIR, re.sub(r'\.wav|\.mp3', ".txt", audio_name))
        text_file = open(text_path, encoding="utf-8", mode="w")
        text_file.write(self.text)
        text_file.close()