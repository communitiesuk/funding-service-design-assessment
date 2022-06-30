import ast
from dataclasses import dataclass
from typing import Dict
from typing import List

from .question import Question


@dataclass
class StructuredQuestionView:

    """
    Provide a standardised data input for question data using the 
    'structured view' template.

    ast.literal_eval: Safely evaluate an expression node or a string
    containing a Python literal or container display. The string or
    node provided may only consist of the following Python literal
    structures: strings, bytes, numbers, tuples, lists, dicts, sets,
     booleans, None, bytes and sets.
    """

    title: str
    answers_per_question: Dict[str, List]  # {question: [answers],}

    @classmethod
    def from_question_json(cls, question_json):
        question = Question.from_json(question_json)
        answers_per_question = {}
        for question_field in question.fields:
            answer = question_field.answer
            try:
                if type(ast.literal_eval(answer)) == list:
                    answers_per_question[
                        question_field.title
                    ] = ast.literal_eval(answer)
                    continue
            except (ValueError, SyntaxError):
                # literal_eval cannot parse string values
                pass
            answers_per_question[question_field.title] = [answer]

        return StructuredQuestionView(question.title, answers_per_question)
