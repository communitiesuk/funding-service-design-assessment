from typing import List
from .question import Question
from datetime import datetime


class Application(object):

    def __init__(
            self,
            identifier: str,
            submitted: datetime,
            fund_name: str,
            questions: List[Question] = None,
    ):
        self.identifier = identifier
        self.submitted = submitted
        self.fund_name = fund_name
        self.questions = questions

    @staticmethod
    def from_json(data: dict):
        application = Application(
            identifier=data.get("id"),
            submitted=datetime.fromisoformat(data.get("date_submitted")),
            fund_name=data.get("fund_name")
        )
        if "questions" in data:
            for question_data in data["questions"]:
                question = Question.from_json(question_data)
                application.add_question(question)

        return application

    def add_question(self, question: Question):
        if not self.questions:
            self.questions = []
        self.questions.append(question)

    def get_question(self, index: int):
        if self.questions:
            return self.questions[index]
        return None
