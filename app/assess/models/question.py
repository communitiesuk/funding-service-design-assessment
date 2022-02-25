from typing import List
from .question_field import QuestionField
from .assessor_field import AssessorField


class Question(object):

    def __init__(
            self,
            title: str,
            fields: List[QuestionField] = None,
            assessor_fields: List[AssessorField] = None
    ):
        self.title = title
        self.fields = fields
        self.assessor_fields = assessor_fields

    @staticmethod
    def default_assessor_fields():
        return [
            {
                "name": "score",
                "field_type": "SelectField",
                "label": "Score",
                "placeholder_text": "",
                "help_text": "Please score this applicant's response out of 5",
                "hint": "",
                "required": "Please enter a score",
                "classes": None,
                "choices": [
                    {"value": "", "text": ""},
                    {"value": 0, "text": "0"},
                    {"value": 1, "text": "1"},
                    {"value": 2, "text": "2"},
                    {"value": 3, "text": "3"},
                    {"value": 4, "text": "4"},
                    {"value": 5, "text": "5"}
                ],
                "choices_type": "number"
            },
            {
                "name": "assessment",
                "field_type": "MultilineTextField",
                "label": "Comments",
                "placeholder_text": "",
                "help_text": "",
                "hint": "",
                "required": "Please enter your assessment",
                "classes": None,
                "choices": None,
                "choices_type": None
            }
        ]

    @staticmethod
    def from_json(data: dict):
        question = Question(
            title=data.get("question")
        )
        if "fields" in data:
            for field_data in data["fields"]:
                field = QuestionField.from_json(field_data)
                question.add_field(field)

        if len(Question.default_assessor_fields()) > 0:
            for field_data in Question.default_assessor_fields():
                field = AssessorField.from_json(field_data)
                question.add_assessor_field(field)
        return question

    def add_assessor_field(self, field: AssessorField):
        if not self.assessor_fields:
            self.assessor_fields = []
        self.assessor_fields.append(field)

    def add_field(self, field: QuestionField):
        if not self.fields:
            self.fields = []
        self.fields.append(field)
