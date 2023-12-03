import openai
from config import Answer, get_gpt_request_cost
import os
from dotenv import load_dotenv

loaded_env = load_dotenv("../.env")
if not load_dotenv:
    exit("Создайте файл с переменными окружения в корневой директории .env")

GPT_TOKEN = os.getenv("GPT_TOKEN")
GPT_MODEL = "gpt-3.5-turbo-16k-0613"

def get_answer_from_gpt(query: str) -> Answer | str:
    openai.api_key = GPT_TOKEN
    try:
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": query,
                },
            ],
        )
    except BaseException as err:
        return f"Не удалось подключиться к GPT. Текст ошибки: {err}"

    question_tokens = response.usage.prompt_tokens
    answer_tokens = response.usage.completion_tokens
    return Answer(
        Question=query,
        Text=[i["message"]["content"] for i in response["choices"]][0],
        AnswerTokens=answer_tokens,
        QuestionTokens=question_tokens,
        Cost=get_gpt_request_cost(question_tokens, answer_tokens)
    )

def get_test_for_text(text: str) -> Answer | None:
    question = f"Мне нужно проверить своих студентов на знание вот этого текста: `{text}`\nСоставь тест из 10 вопросов с вариантами ответов в такой структуре: 1. Вопрос\na) первый вариант\nb) второй вариант\nc) третий вариант\nd) четвертый вариант\nОтвет: полный вариант"
    answer = get_answer_from_gpt(question)
    if isinstance(answer, Answer):
        return answer
    
    print(f"GPT error: {answer}")
    return None
