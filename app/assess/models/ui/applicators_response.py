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


def _ui_component_from_factory(item: dict):
    presentation_type = item["presentation_type"]
    if presentation_type == "grouped_fields":
        return MonetaryKeyValues.from_dict(item)
    elif presentation_type == "text":
        return OrientedQuestionAnswerPair.from_dict(item)
    elif presentation_type == "file":
        return FileQuestionAnswerPair.from_dict(item)

    # Note that types "amount", "description" and "heading" are not used
    # here because they are grouped together in the "grouped_fields" type
    # in a pre-processing step
    raise NotImplementedError(
        f"Unknown presentation type: {presentation_type}"
    )


def _convert_heading_description_amount_items(
    response,
) -> tuple[list[dict], set[str]]:
    field_ids = {
        item["field_id"]
        for item in response
        if item["presentation_type"] == "heading"
    }

    grouped_fields_items = []
    for field_id in field_ids:
        items_map = {
            item["presentation_type"]: item
            for item in response
            if item["field_id"] == field_id
        }
        descriptions, amounts = (
            items_map.get("description")["answer"],
            items_map.get("amount")["answer"],
        )
        grouped_fields = zip(descriptions, map(float, amounts))

        grouped_fields_items.append(
            {
                "caption": items_map.get("heading")["question"],
                "question": items_map.get("description")["question"],
                "field_id": field_id,
                "answer": grouped_fields,
                "presentation_type": "grouped_fields",
            }
        )
    return grouped_fields_items, field_ids


def _convert_checkbox_items(response) -> tuple[list[dict], set[str]]:
    def _dash_separated_to_human_readable(s: str) -> str:
        return s.replace("-", " ").capitalize()

    field_ids = {
        item["field_id"]
        for item in response
        if item["field_type"] == "checkboxesField"
    }
    items_to_process = (i for i in response if i["field_id"] in field_ids)

    text_items = []
    for item in items_to_process:
        text_items.extend(
            {
                "question": _dash_separated_to_human_readable(answer),
                "field_id": item["field_id"],
                "answer": "Yes",
                "presentation_type": "text",
            }
            for answer in item["answer"]
        )
    return text_items, field_ids


def _make_field_ids_hashable(item: dict) -> dict:
    field_id = item["field_id"]
    if isinstance(field_id, list):
        item["field_id"] = tuple(field_id)
    return item


def create_ui_components(
    response_with_unhashable_fields: list[dict],
) -> List[ApplicationResponseComponent]:
    response = map(_make_field_ids_hashable, response_with_unhashable_fields)

    (
        grouped_fields_items,
        gfi_field_ids,
    ) = _convert_heading_description_amount_items(response)
    text_items, ti_field_ids = _convert_checkbox_items(response)

    processed_field_ids = gfi_field_ids | ti_field_ids
    unprocessed_items = [
        i for i in response if str(i["field_id"]) not in processed_field_ids
    ]

    post_processed_items = (
        grouped_fields_items + text_items + unprocessed_items
    )
    # note that we use dict.fromkeys to remove duplicates
    # (sets are unordered)
    field_ids_in_order = list(
        dict.fromkeys(str(i["field_id"]) for i in response)
    )
    # we need to preserve the order of the fields from the back-end,
    # so we re-sort it here
    post_processed_items.sort(
        key=lambda x: field_ids_in_order.index(str(x["field_id"]))
    )

    return map(_ui_component_from_factory, post_processed_items)
