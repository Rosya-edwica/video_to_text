from pymongo import MongoClient
from datetime import datetime
from tools import ResponseGPT, Test

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
            "date": datetime.now(),
            "text": transcribation
        })
    
    def save_gpt_responce(self, video_name: str, response: ResponseGPT):
        self.gpt_responces_cls.insert_one({
            "video_name": video_name,
            "date": datetime.now(),
            "request": response.Question,
            "text": response.Text,
            "cost": response.Cost,
            "request_tokens": response.QuestionTokens,
            "answer_tokens": response.AnswerTokens
        })
        self.save_transcribation(video_name, response.Text)

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
            "date": datetime.now(),
            "test": test_json
        })
