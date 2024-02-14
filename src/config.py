from typing import NamedTuple
import re
import json

# Стоимость модели gpt-4-1106-preview с официального сайта: https://openai.com/pricing 
QUESTION_TOKEN_PRICE = 0.01 / 1000
ANSWER_TOKEN_PRICE = 0.03 / 1000

class Cost(NamedTuple):
    Dollar: float
    Dollar_1000: float

class Answer(NamedTuple):
    Question: str
    Text: str
    Cost: Cost
    QuestionTokens: int
    AnswerTokens: int

class Question(NamedTuple):
    Text: str
    Answer: str
    Choices: list[str]


class Test(NamedTuple):
    Questions: list[Question]


def parse_test(text: str) -> Test:
    

    list_of_questions_text = text.split("\n\n")
    questions: list[Question] = []

    for qst_text in list_of_questions_text:
        questions.append(parse_question(qst_text))
    return Test(Questions=questions)

def parse_question(text: str) -> Question:
    title_pattern = r"\d+. .*?\n|\d+.*\n"
    title_pattern_sub = r"\d+.|\n|Вопрос:"
    
    return Question(
        Text=re.sub(title_pattern_sub, "", re.findall(title_pattern, text)[0]).strip(),
        Answer=parse_answer(text),
        Choices=parse_choices(text)
    )

def parse_answer(text: str) -> str:
    answer_pattern = r"Ответ:.*|\w\) .*\( ответ \)"
    answer_pattern_sub = r"Ответ: |\n|\( ответ \)|\w\) "
    answer = re.sub(answer_pattern_sub, "", re.findall(answer_pattern, text)[0]).strip()
    return answer


def parse_choices(text: str) -> list[str]:
    choices_pattern = r"\w\) .*"
    choices_pattern_sub = r"\w\) |\n|\( ответ \)"

    choices = []
    for item in re.findall(choices_pattern, text):
        choice = re.sub(choices_pattern_sub, "", item)
        choices.append(choice.strip())
    return choices


def save_test_to_json(test: Test, filename: str):
    data = []
    for qst in test.Questions:
        data.append({
            "question": qst.Text,
            "answer": qst.Answer,
            "choices": qst.Choices
        })


    with open(f"data/answers/{filename}", mode="w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



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




if __name__ == "__main__":
    data = open("data/answers/dofamine.txt", mode="r", encoding="utf-8") 
    save_test_to_json(parse_test(data.read()))
