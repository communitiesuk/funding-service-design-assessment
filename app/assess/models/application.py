from dataclasses import dataclass
from datetime import datetime
from typing import List

from .question import Question


@dataclass
class Application:
    identifier: str
    submitted: datetime
    fund_name: str
    questions: List[Question] = None
    status: str = "not started"
    assessment_deadline: datetime = datetime.now()

    @staticmethod
    def from_json(data: dict):
        application = Application(
            identifier=data.get("id"),
            submitted=datetime.fromisoformat(
                data.get("date_submitted", "1970-01-01")
            ),
            fund_name=data.get("fund_name"),
            status=data.get("status"),
            assessment_deadline=datetime.fromisoformat(
                data.get("assessment_deadline", "1970-01-01")
            ),
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
