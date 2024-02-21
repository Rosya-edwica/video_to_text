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


from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip
import math

@tools.stopwatch_decorator
def video_to_chunks(video_path: str) -> list[str]:
    video = VideoFileClip(video_path)
    duration = video.duration
    segment_duration = 60
    os.makedirs(name="data/chunks/", exist_ok=True)

    num_segments = math.ceil(duration / segment_duration)
    chunks_files = []
    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = (i + 1) * segment_duration if (i + 1) * segment_duration < duration else duration
        segment_filename = f"data/videos/segment_{i}.mp4"
        audio_filename = f"data/chunks/audio_{i}.mp3"
        ffmpeg_extract_subclip(video_path, start_time, end_time, targetname=segment_filename)

        segment = VideoFileClip(segment_filename)
        segment.audio.write_audiofile(audio_filename)
        os.remove(segment_filename)
        chunks_files.append(audio_filename)
    os.remove(video_path)
    print(chunks_files)
    return chunks_files
