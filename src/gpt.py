from openai import OpenAI
from config import Answer, get_gpt_request_cost
import os
from dotenv import load_dotenv


loaded_env = load_dotenv("../.env")
if not load_dotenv:
    exit("Создайте файл с переменными окружения в корневой директории .env")

GPT_TOKEN = os.getenv("GPT_TOKEN")
GPT_MODEL = "gpt-4-1106-preview"
ANSWERS_FOLDER = "data/answers/"


def create_test_by_text(query: str, text: str) -> Answer | None:
    """
    query: Промт для получения теста
    text: Текст по которому нужно составить тест
    """

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
    return Answer(
        Question=query,
        Text=response.choices[0].message.content,
        AnswerTokens=answer_tokens,
        QuestionTokens=question_tokens,
        Cost=get_gpt_request_cost(question_tokens, answer_tokens)
    )


def transcribe_audio(path: str) -> str:
    """
    transcribe_audio() с помощью API openAI достает текст из .mp3-аудиофайла
    """
    audio_file = open(path, mode="rb")
    client = OpenAI(api_key=GPT_TOKEN)
    answer = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    return answer.text


def save_answer(text: str, filename: str):
    """Сохраняем ответ пока в файл, потом будем сохранять в бд"""
    
    os.makedirs(ANSWERS_FOLDER, exist_ok=True)
    file = open(os.path.join(ANSWERS_FOLDER, filename), mode="w", encoding="utf-8")
    file.write(text)
    file.close()