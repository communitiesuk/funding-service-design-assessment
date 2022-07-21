from dataclasses import dataclass


@dataclass
class AssessmentFlow:
    section_name: list
    questions: list
    question: list
    fields: list

    @staticmethod
    def as_json(assessment_json, page_index):
        return AssessmentFlow(
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
    def get_section_name(assessment_json, page_index):
        return assessment_json["sections"][page_index]["section_name"]

    @staticmethod
    def get_questions(assessment_json, page_index):
        questions = []
        sections = assessment_json["sections"][page_index]
        for section in sections["questions"]:
            questions.append(section)
        return questions

    def get_question(assessment_json, page_index):
        get_questions = AssessmentFlow.get_questions(
            assessment_json, page_index
        )
        question = []
        for q in get_questions:
            question.append(q["question"])
        return question

    @staticmethod
    def get_fields(assessment_json, page_index):
        fields = []
        get_fields = AssessmentFlow.get_questions(assessment_json, page_index)

        for field in get_fields:
            fields.append(field["fields"])
        return fields

    @staticmethod
    def get_page_index(page_index: str, sections: list) -> int:

        if not page_index or page_index <= str(0):
            page_index = int(0)

        elif page_index > str(len(sections) - 1):
            page_index = int(len(sections) - 1)

        return int(page_index)
