from dataclasses import dataclass
from typing import List

from .question_field import QuestionField


@dataclass
class Question:
    title: str
    fields: List[QuestionField] = None

    @staticmethod
    def from_json(data: dict):
        question = Question(title=data.get("question"))
        if "fields" in data:
            for field_data in data["fields"]:
                field = QuestionField.from_json(field_data)
                question.add_field(field)

        return question

    def add_field(self, field: QuestionField):
        if not self.fields:
            self.fields = []
        self.fields.append(field)


@dataclass
class QuestionAnswerPage:
    @staticmethod
    def get_questions(page_title, questions_page):
        questions = []
        for data in questions_page:
            if page_title == data.title:
                for field in data.fields:
                    questions.append(field.title)
        return tuple(questions)

    @staticmethod
    def get_answers(page_title, answers_page):
        answers = []
        for data in answers_page:
            if page_title == data.title:
                for field in data.fields:
                    answers.append(field.answer)
        return tuple(answers)
