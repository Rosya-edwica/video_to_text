from openai import OpenAI
from tools import ResponseGPT, calculate_gpt_request_cost
import os
from dotenv import load_dotenv


loaded_env = load_dotenv("../.env")
if not load_dotenv:
    exit("Создайте файл с переменными окружения в корневой директории .env")

GPT_TOKEN = os.getenv("GPT_TOKEN")
GPT_MODEL = "gpt-4-1106-preview"
ANSWERS_FOLDER = "data/answers/"
GPT_MIN_PRICE = 0.006


def create_test_by_text(query: str, text: str) -> ResponseGPT | None:
    """
    query: Промт для получения теста
    text: Текст по которому нужно составить тест
    """
    print("Генерируем тест по тексту...")
    client = OpenAI(api_key=GPT_TOKEN)
    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": query,
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
        )
    except BaseException as err:
        print(f"Не удалось подключиться к GPT. Текст ошибки: {err}")
        return

    question_tokens = response.usage.prompt_tokens
    answer_tokens = response.usage.completion_tokens
    return ResponseGPT(
        Question=query,
        Text=response.choices[0].message.content,
        AnswerTokens=answer_tokens,
        QuestionTokens=question_tokens,
        Cost=calculate_gpt_request_cost(question_tokens, answer_tokens)
    )

def transcribe_audio(path: str) -> str:
    """
    transcribe_audio() с помощью API openAI достает текст из .mp3-аудиофайла
    """
    audio_file = open(path, mode="rb")
    client = OpenAI(api_key=GPT_TOKEN)
    answer = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        prompt="Сократи текст максимально, чтобы при этом сохранить главную суть и факты. Лишние слова и воду нужно убрать"
    )
    return answer.text
