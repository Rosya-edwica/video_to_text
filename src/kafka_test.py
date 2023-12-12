from kafka import KafkaProducer

class NewProducer:
    def __init__(self):
        try:
            self.producer = KafkaProducer(bootstrap_servers="localhost:9092")
        except:
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