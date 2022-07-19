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
    
    
    @staticmethod
    def get_page_index(page_index: str, sections: list) -> int:
        
        if not page_index or page_index <= str(0):
            page_index = int(0)
        elif page_index > str(len(sections)):
            page_index = int(len(sections))
               
        return int(page_index)