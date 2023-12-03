from typing import NamedTuple


# Стоимость модели gpt-3.5-turbo-1106 с официального сайта: https://openai.com/pricing 
QUESTION_TOKEN_PRICE = 0.0010 / 1000
ANSWER_TOKEN_PRICE = 0.0020 / 1000

class Cost(NamedTuple):
    Dollar: float
    Dollar_1000: float

class Answer(NamedTuple):
    Question: str
    Text: str
    Cost: Cost
    QuestionTokens: int
    AnswerTokens: int


def get_gpt_request_cost(question_tokens: int, answer_tokens: int) -> Cost:
    """
    Функция рассчитывает примерную стоимость запроса в долларах с помощью количества потраченных токенов
    """
    dollar_cost = question_tokens * QUESTION_TOKEN_PRICE + answer_tokens * ANSWER_TOKEN_PRICE
    dollar_cost_1000 = dollar_cost * 1000

    return Cost(
        Dollar=round(dollar_cost, 5),
        Dollar_1000=round(dollar_cost_1000, 3),
    )