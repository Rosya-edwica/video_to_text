import re
from tools.models import Test, Question, RequestCost, VideoUrl
import wget
import os
import logging
import csv
import time

# Стоимость модели gpt-4-1106-preview с официального сайта: https://openai.com/pricing 
QUESTION_TOKEN_PRICE = 0.01 / 1000
ANSWER_TOKEN_PRICE = 0.03 / 1000


def parse_test(text: str) -> Test:
    """Оборачиваем текст теста в структуру Test с помощью регулярных выражений"""

    list_of_questions_text = text.split("\n\n")
    questions: list[Question] = []

    for qst_text in list_of_questions_text:
        questions.append(parse_question(qst_text))
    return Test(Questions=questions)


def parse_question(text: str) -> Question:
    """Оборачиваем текст вопроса в структуру Question с помощью регулярных выражений"""
    title_pattern = r"\d+. .*?\n|\d+.*\n"
    title_pattern_sub = r"\d+.|\n|Вопрос:"
    
    return Question(
        Text=re.sub(title_pattern_sub, "", re.findall(title_pattern, text)[0]).strip(),
        Answer=parse_answer(text),
        Choices=parse_choices(text)
    )

def parse_answer(text: str) -> str:
    """Получаем текст ответа на вопрос помощью регулярных выражений"""

    answer_pattern = r"Ответ:.*|\w\) .*\( ответ \)"
    answer_pattern_sub = r"Ответ: |\n|\( ответ \)|\w\) "
    answer = re.sub(answer_pattern_sub, "", re.findall(answer_pattern, text)[0]).strip()
    return answer

def parse_choices(text: str) -> list[str]:
    """Получаем список вариантов ответов с помощью регулярных выражений"""
    choices_pattern = r"\w\) .*"
    choices_pattern_sub = r"\w\) |\n|\( ответ \)"
    choices = []
    for item in re.findall(choices_pattern, text):
        choice = re.sub(choices_pattern_sub, "", item)
        choices.append(choice.strip())
    # Регулярка может захватить два раза ответ в список, поэтому возвращаем уникальный список
    return list(set(choices))

def calculate_gpt_request_cost(question_tokens: int, answer_tokens: int) -> RequestCost:
    """
    Функция рассчитывает примерную стоимость запроса в долларах с помощью количества потраченных токенов
    """
    dollar_cost = question_tokens * QUESTION_TOKEN_PRICE + answer_tokens * ANSWER_TOKEN_PRICE
    dollar_cost_1000 = dollar_cost * 1000

    return RequestCost(
        Dollar=round(dollar_cost, 5),
        DollarThousand=round(dollar_cost_1000, 3),
    )


def stopwatch_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        logging.info(f"{round(end_time - start_time)} сек. столько выполнялась функции: {func.__name__} с аргументами ({args})")
        return result

    return wrapper

@stopwatch_decorator
def download_video(url: str, path: str):
    logging.info(f"Пытаемся скачать файл: {path} по ссылке: {url}")
    wget.download(url, path)
    print(f"Скачали видео в '{path}'")


def get_videos_from_csv(path) -> list[VideoUrl]:
    if not os.path.isfile(path):
        print(f"Внимание: файл '{path}' не существует")
        return []
    with open(path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        data = [VideoUrl(row[0].replace("/", "_"), row[1], row[2]) for idx, row in enumerate(reader) if idx > 0] # не берем заголовок
    return data

