import speech_recognition as sr
import os
import shutil
from pydub import AudioSegment
from pydub.silence import split_on_silence
from time import perf_counter

CHUNKS_DIR = "data/chunks/"
TEXT_DIR = "data/text/"

def transcribe_large_audio(audio_path: str) -> str:
    """
    Input: audio_path format .wav
    Output: text
    """
    text = check_result_for_audio_exists(audio_path)
    if text:
        return text

    start = perf_counter()
    sound = AudioSegment.from_wav(audio_path)
    # Дробим аудио на мелкие части
    chunks = split_on_silence(sound, min_silence_len=700, silence_thresh=sound.dBFS-14, keep_silence=700)
    
    # Создаем временную папку, куда будем сохранять кусочки аудио
    os.makedirs(name=CHUNKS_DIR, exist_ok=True) 
    r = sr.Recognizer()    
    text_result = ""
    for i, audio_chunk in enumerate(chunks, start=1):
        # Создаем кусочек и сохраняем его в файлик
        chunk_filename = os.path.join(CHUNKS_DIR, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")

        # Пытаемся прочитать наш кусочек аудио
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            try:
                text = r.recognize_google(audio_listened, language="ru-RU")
            except sr.UnknownValueError as e:
                print("Error:", str(e))
            else:
                print(chunk_filename, ":", text)
                text_result += text
   
    # Сохраняем результат, чтобы в следующий раз не тратить много времени
    save_text(audio_path, text_result)
    # Удаляем временную папку
    shutil.rmtree(CHUNKS_DIR)
    print(f"Время на транскрибацию аудио: {perf_counter() - start} сек.")
    return text_result

def check_result_for_audio_exists(audio_path: str) -> str | None:
    """
    Транскрибация длинного аудио занимает много времени, поэтому нам лучше лишний раз проверить
    не сохраняли ли мы раньше результат по нашему аудио
    """
    audio_name = audio_path.split("/")[-1]
    text_path = os.path.join(TEXT_DIR, audio_name.replace(".wav", ".txt"))
    if os.path.exists(text_path):
        text_file = open(text_path, mode="r", encoding="utf-8")
        text = text_file.read()
        text_file.close()
        return text
    
    return None

def save_text(audio_path: str, text: str) -> None:
    os.makedirs(name=TEXT_DIR, exist_ok=True)
    audio_name = audio_path.split("/")[-1]
    text_path = os.path.join(TEXT_DIR, audio_name.replace(".wav", ".txt"))
    text_file = open(text_path, encoding="utf-8", mode="w")
    text_file.write(text)
    text_file.close()
