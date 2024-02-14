"""Данный модуль является необязательным, т.к его роль заключается в подсчете потраченных денег на запросы GPT
Кафка используется для того, чтобы отправлять все в единое хранилище запросов GPT, куда складываются все запросы из
разных программ.
Использование кафки необязательно и использовалось мной в образовательных и практических целях.
"""

from kafka import KafkaProducer


class NewProducer:
    """Кафка запускается отдельно на сервере, тк существует отдельно от этого проекта и не зависит от него.
    Поэтому если не получается подключиться к кафке, значит глобально кафка не запущена и писать туда смысла нет"""
    def __init__(self):
        try:
            self.producer = KafkaProducer(bootstrap_servers="localhost:9092")
        except BaseException:
            self.producer = None
        self.topic = "gpt-cost"

    def send_to_text_partition(self, message: str):
        if not self.producer:
            return
        self.producer.send(
            self.topic,
            message.encode("utf-8"),
            partition=0
        )

    def send_to_audio_partition(self, message: str):
        if not self.producer:
            return
        self.producer.send(
            self.topic,
            message.encode("utf-8"),
            partition=1
        )