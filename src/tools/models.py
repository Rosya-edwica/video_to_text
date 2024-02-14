"""Основные сущности программы"""
from typing import NamedTuple


class RequestCost(NamedTuple):
    Dollar: float
    DollarThousand: float


class ResponseGPT(NamedTuple):
    Question: str
    Text: str
    Cost: RequestCost
    QuestionTokens: int
    AnswerTokens: int


class Question(NamedTuple):
    Text: str
    Answer: str
    Choices: list[str]


class Test(NamedTuple):
    Questions: list[Question]