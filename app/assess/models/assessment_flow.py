from dataclasses import dataclass


@dataclass
class AssessmentFlow:
    sections: list
    questions: list
    question: dict
    fields: list
    title: str
    answer: str

    @staticmethod
    def as_json(assessment_json):
        sections = assessment_json["sections"]
        questions = [section["questions"] for section in sections]
        # question_titles = [question[0] for question in questions]

        return questions
