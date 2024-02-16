from moviepy.editor import VideoFileClip
from typing import Literal
import os
import tools

AUDIO_DIR = "data/audio/"


@tools.stopwatch_decorator
def video_to_audio(video_path: str, audio_format: list[Literal["mp3", "wav"]]):
    """
    Input: video_path .mp4 format
    Output: audio_path .mp3/.wav format
    """
    print(f"Извлекаем аудио из видео '{video_path}...'")
    os.makedirs(AUDIO_DIR, exist_ok=True)
    if audio_format not in ("mp3", "wav"):
        exit("Неправильный формат для аудиофайла. Вы можете выбрать только mp3 или wav")

    # Загружаем видео
    video = VideoFileClip(video_path)
    # Достаем из видео аудио-дорожку 
    audio_file = video.audio
    # Получаем название файла видео без расширения и директорий
    video_name = video_path.split("/")[-1].replace(".mp4", f".{audio_format}")
    # Даем название аудиофайлу как у видео
    audio_path = os.path.join(AUDIO_DIR, video_name) 
    # Сохраняем аудио
    audio_file.write_audiofile(audio_path) 

    os.remove(video_path) # Очищаем память
    print(f"Извлекли аудио и удалили видео '{video_path}...'")
    #  Возвращаем путь
    return audio_path
