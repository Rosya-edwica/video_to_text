from moviepy.editor import VideoFileClip
import os

AUDIO_DIR = "data/audio/"

def video_to_audio(video_path: str) -> str:
    """
    Input: video_path .mp4 format
    Output: audio_path .wav format
    """
    os.makedirs(AUDIO_DIR, exist_ok=True)

    # Загружаем видео
    video = VideoFileClip(video_path)
    # Достаем из видео аудио-дорожку 
    audio_file = video.audio 
    # Получаем название файла видео без расширения и директорий
    video_name = video_path.split("/")[-1].replace(".mp4", ".wav") 
     # Даем название аудиофайлу как у видео
    audio_path = os.path.join(AUDIO_DIR, video_name) 
    # Сохраняем аудио
    audio_file.write_audiofile(audio_path) 

    #  Возвращаем путь
    return audio_path 