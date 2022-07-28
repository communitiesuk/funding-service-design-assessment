from dataclasses import dataclass


@dataclass
class AssessmentFlow:
    sections: list
    section_name: list
    questions: list
    question: list
    fields: list

    @staticmethod
    def as_json(assessment_json, page_index):
        return AssessmentFlow(
            sections=AssessmentFlow.get_sections(assessment_json),
            section_name=AssessmentFlow.get_section_name(
                assessment_json, page_index
            ),
            questions=AssessmentFlow.get_questions(
                assessment_json, page_index
            ),
            question=AssessmentFlow.get_question(assessment_json, page_index),
            fields=AssessmentFlow.get_fields(assessment_json, page_index),
        )

    @staticmethod
    def get_sections(data):
        return data["sections"]

    @staticmethod
    def get_section_name(data, page_index):
        return data["sections"][page_index]["section_name"]

    @staticmethod
    def get_questions(data, page_index):
        questions = []
        sections = data["sections"][page_index]
        for section in sections["questions"]:
            questions.append(section)
        return questions

    def get_question(data, page_index):
        get_questions = AssessmentFlow.get_questions(data, page_index)
        question = []
        for questions in get_questions:
            question.append(questions["question"])
        return question

    @staticmethod
    def get_fields(data, page_index):
        fields = []
        get_fields = AssessmentFlow.get_questions(data, page_index)
        for field in get_fields:
            fields.append(field["fields"])
        return fields

    @staticmethod
    def process_index(index: str, data: list) -> int:
        sections = AssessmentFlow.get_sections(data)
        if int(index) > int(len(sections) - 1):
            index = int(len(sections) - 1)
        return int(index)
