from dataclasses import dataclass
from typing import List

from .question_field import QuestionField


@dataclass
class Question:
    title: str
    status: str
    fields: List[QuestionField] = None

    @staticmethod
    def from_json(data: dict):
        question = Question(
            title=data.get("question"), status=data.get("status")
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
