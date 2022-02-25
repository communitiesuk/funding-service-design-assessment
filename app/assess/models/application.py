from datetime import datetime
from typing import List
from dataclasses import dataclass
from .question import Question


@dataclass
class Application:
    identifier: str
    submitted: datetime
    fund_name: str
    questions: List[Question] = None

    @staticmethod
    def from_json(data: dict):
        application = Application(
            identifier=data.get("id"),
            submitted=datetime.fromisoformat(data.get("date_submitted")),
            fund_name=data.get("fund_name"),
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
