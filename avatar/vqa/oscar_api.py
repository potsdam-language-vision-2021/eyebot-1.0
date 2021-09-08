from dataclasses import dataclass
import requests
import urllib.parse


@dataclass
class OscarModel:
    endpoint: str

    def answer_question(self, image_id, question):
        params = {"image": image_id, "question": question}
        req = requests.get(urllib.parse.urljoin(self.endpoint, "answer_question"), params=params)
        return req.json()

    def get_caption(self, image_id):
        params = {"image": image_id}
        req = requests.get(urllib.parse.urljoin(self.endpoint, "get_caption"), params=params)
        return req.json()