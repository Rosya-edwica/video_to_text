from pymongo import MongoClient
from datetime import datetime
from tools import ResponseGPT, Test
import json

class Mongo:
    def __init__(self, connection_url: str = "mongodb://localhost:27017/"):
        self.client = MongoClient(connection_url)
        self.db = self.client["fosagro"]
        self.transcribations_clc = self.db["transcribations"]
        self.gpt_responces_cls = self.db["gpt_responces"]
        self.tests_cls = self.db["tests"]

    
    def save_transcribation(self, video_name: str, transcribation: str):
        self.transcribations_clc.insert_one({
            "video_name": video_name,
            "date": get_current_date(),
            "text": transcribation
        })
    
    def save_gpt_responce(self, video_name: str, response: ResponseGPT):
        self.gpt_responces_cls.insert_one({
            "video_name": video_name,
            "date": get_current_date(),
            "request": response.Question,
            "text": response.Text,
            "cost": response.Cost,
            "request_tokens": response.QuestionTokens,
            "answer_tokens": response.AnswerTokens
        })

    def save_test(self, video_name: str, test: Test):
        test_json = []
        for i in test.Questions:
            test_json.append({
                "question": i.Text,
                "answer": i.Answer,
                "choices": i.Choices
            })
        self.tests_cls.insert_one({
            "video_name": video_name,
            "date": get_current_date(),
            "test": test_json
        })
    
    def download_all(self):
        data = [i for i in self.tests_cls.find({})]
        with open("mongo_tests.json", mode="w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        data = [i for i in self.transcribations_clc.find({})]
        with open("mongo_transcribations.json", mode="w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        data = [i for i in self.gpt_responces_cls.find({})]
        with open("mongo_gpt_responces.json", mode="w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def get_current_date() -> str:
    now = datetime.now()
    return now.strftime("%d.%m.%Y %H:%M")