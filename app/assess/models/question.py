from typing import List
from .question_field import QuestionField


class Question(object):

    def __init__(
            self,
            title: str,
            fields: List[QuestionField] = None
    ):
        self.title = title
        self.fields = fields

    @staticmethod
    def from_json(data: dict):
        question = Question(
            title=data.get("question")
        )
        if "fields" in data:
            for field_data in data["fields"]:
                field = QuestionField.from_json(field_data)
                question.add_field(field)
        return question

    def add_field(self, field: QuestionField):
        if not self.fields:
            self.fields = []
        self.fields.append(field)
