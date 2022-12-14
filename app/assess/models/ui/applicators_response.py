from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import List
from typing import Tuple


@dataclass
class ApplicationResponseComponent(ABC):
    @property
    @abstractmethod
    def key(self):
        raise NotImplementedError(
            f"key not implemented for {self.__class__.__name__}"
        )

    @property
    @abstractmethod
    def should_render(self):
        return True


@dataclass
class QuestionAnswerPair(ApplicationResponseComponent, ABC):
    question: str
    answer: str

    @property
    def should_render(self):
        return self.question is not None and self.answer is not None


@dataclass
class FileQuestionAnswerPair(QuestionAnswerPair):
    file_href: str

    @property
    def key(self):
        return "question_with_file_answer"

    @classmethod
    def from_dict(cls, _dict: dict):
        answer = _dict.get("answer")
        return cls(question=_dict["question"], answer=answer, file_href=answer)


@dataclass
class OrientedQuestionAnswerPair(QuestionAnswerPair):
    _orientation: str

    @property
    def key(self):
        if self._orientation == "above":
            return "question_above_answer"
        return "question_beside_answer"

    @classmethod
    def from_dict(cls, _dict: dict):
        return cls(
            question=_dict["question"],
            answer=_dict.get("answer"),
            _orientation="above"
            if _dict.get("field_type") == "multilineTextField"
            else "beside",
        )


@dataclass
class MonetaryKeyValues(ApplicationResponseComponent):
    caption: str
    column_description: str
    question_answer_pairs: List[Tuple[str, float]]
    total: float

    @property
    def should_render(self):
        return (
            self.question_answer_pairs and len(self.question_answer_pairs) > 0
        )

    @property
    def key(self):
        return "monetary_key_values"

    @classmethod
    def from_dict(cls, _dict: dict):
        return cls(
            caption=_dict.get("caption", ""),  # sometimes not present
            column_description=_dict["question"],
            question_answer_pairs=_dict["answer"],
            total=sum([float(amt) for _, amt in _dict["answer"]]),
        )
