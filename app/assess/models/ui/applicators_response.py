from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from typing import Iterable
from typing import List
from typing import Tuple

from app.assess.views.filters import format_address
from app.assess.views.filters import format_date
from app.assess.views.filters import remove_dashes_underscores_capitalize
from app.assess.data import get_file_url

ANSWER_NOT_PROVIDED_DEFAULT = "Not provided."


@dataclass
class ApplicatorsResponseComponent(ABC):
    @property
    @abstractmethod
    def key(self):
        raise NotImplementedError(
            f"key not implemented for {self.__class__.__name__}"
        )

    @property
    def should_render(self):
        return True


@dataclass
class QuestionHeading(ApplicatorsResponseComponent):
    question: str

    key = "question_heading"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(question=data["question"])


@dataclass
class QuestionAnswerPair(ApplicatorsResponseComponent):
    question: str
    answer: str | float

    @property
    def should_render(self):
        return True

    @classmethod
    def from_dict(cls, data: dict):
        answer = data.get("answer")
        return cls(
            question=data["question"],
            answer=answer if answer else ANSWER_NOT_PROVIDED_DEFAULT,
        )


class AboveQuestionAnswerPair(QuestionAnswerPair):
    key = "question_above_answer"


class BesideQuestionAnswerPair(QuestionAnswerPair):
    key = "question_beside_answer"


@dataclass
class QuestionAnswerPairHref(QuestionAnswerPair):
    answer_href: str

    @classmethod
    def from_dict(cls, data: dict, href):  # noqa
        answer = data.get("answer")
        return cls(
            question=data["question"],
            answer=answer if answer else ANSWER_NOT_PROVIDED_DEFAULT,
            answer_href=href if answer else None,
        )


class AboveQuestionAnswerPairHref(QuestionAnswerPairHref):
    key = "question_above_href_answer"


class BesideQuestionAnswerPairHref(QuestionAnswerPairHref):
    key = "question_beside_href_answer"


@dataclass
class FormattedBesideQuestionAnswerPair(QuestionAnswerPair):
    formatter: callable

    key = "question_beside_with_formatted_answer"

    @classmethod
    def from_dict(cls, data: dict, formatter: callable):  # noqa
        return cls(
            question=data["question"],
            answer=data.get("answer", ANSWER_NOT_PROVIDED_DEFAULT),
            formatter=formatter if data.get("answer") else lambda x: x,
        )


@dataclass
class MonetaryKeyValues(ApplicatorsResponseComponent):
    caption: str
    column_description: str
    question_answer_pairs: List[Tuple[str, float]]
    total: float

    key = "monetary_key_values"

    @property
    def should_render(self):
        if not self.question_answer_pairs:
            return False
        return len(self.question_answer_pairs) > 0

    @classmethod
    def from_dict(cls, data: dict):
        caption, question = data["question"]
        return cls(
            caption=caption,  # sometimes not present
            column_description=question,
            question_answer_pairs=[
                (desc, float(amt)) for desc, amt in data["answer"]
            ],
            total=sum([float(amt) for _, amt in data["answer"]]),
        )


def _ui_component_from_factory(item: dict, application_id: str):
    presentation_type = item["presentation_type"]
    field_type = item.get("field_type")
    answer = item.get("answer")

    if answer and field_type in ("numberField",):
        if presentation_type not in ("grouped_fields",):
            item["answer"] = float(item["answer"])

    if presentation_type == "grouped_fields":
        return MonetaryKeyValues.from_dict(item)

    elif presentation_type == "question_heading":
        return QuestionHeading.from_dict(item)

    elif presentation_type in ("text", "list"):

        if field_type in ("multilineTextField",):
            return AboveQuestionAnswerPair.from_dict(item)
        elif field_type in ("websiteField",):
            return BesideQuestionAnswerPairHref.from_dict(item, href=answer)
        elif field_type in ("datePartsField",):
            return FormattedBesideQuestionAnswerPair.from_dict(
                item,
                formatter=lambda x: format_date(
                    x, from_="%Y-%m-%d", to_="%d %B %Y"
                ),
            )
        elif field_type in ("emailAddressField",):
            return BesideQuestionAnswerPairHref.from_dict(
                item, href=f"mailto:{answer}"
            )
        elif field_type in ("telephoneNumberField",):
            return BesideQuestionAnswerPairHref.from_dict(
                item, href=f"tel:{answer}"
            )
        else:
            return BesideQuestionAnswerPair.from_dict(item)

    elif presentation_type == "file":
        # TODO(FS-2065(?)): add href as link to download actual file?
        presighned_url = get_file_url(filename=answer, application_id=application_id)
        return AboveQuestionAnswerPairHref.from_dict(item, href=presighned_url)

    elif presentation_type == "address":
        return FormattedBesideQuestionAnswerPair.from_dict(
            item, format_address
        )

    # Note that types "amount", "description" and "heading" are not used
    # here because they are grouped together in the "grouped_fields" type
    # in a pre-processing step
    raise NotImplementedError(
        f"Unknown presentation type: {presentation_type} for item: {item}"
    )


def _convert_heading_description_amount(
    response: Iterable[dict],
) -> tuple[list[dict], set[str]]:
    field_ids = [
        item["field_id"]
        for item in response
        if item["presentation_type"] == "heading"
    ]

    items = []

    for index, field_id in enumerate(field_ids):
        heading = _get_item_by_presentation_type_index(
            response, "heading", index
        )
        description = _get_item_by_presentation_type_index(
            response, "description", index
        )
        amount = _get_item_by_presentation_type_index(
            response, "amount", index
        )

        if "answer" not in description or "answer" not in amount:
            items.append(_build_item(heading["question"], field_id))
            continue

        descriptions, amounts = description["answer"], amount["answer"]

        poundless_amounts = [a.replace("£", "") for a in amounts]

        grouped_fields = list(zip(descriptions, map(float, poundless_amounts)))

        items.append(
            {
                "question": (heading["question"], description["question"]),
                "field_id": field_id,
                "answer": grouped_fields,
                "presentation_type": "grouped_fields",
            }
        )
    return items, set(field_ids)


def _build_item(question, field_id, presentation_type="text"):
    return {
        "question": question,
        "field_type": "text",
        "field_id": field_id,
        "presentation_type": presentation_type,
    }


def _get_item_by_presentation_type_index(response, presentation_type, index):
    try:
        return next(
            item
            for idx, item in enumerate(
                (
                    item
                    for item in response
                    if item["presentation_type"] == presentation_type
                )
            )
            if idx == index
        )
    except StopIteration:
        raise ValueError(
            "Could not find item with presentation_type:"
            f" {presentation_type} at index: {index}\nThis probably means"
            " there is an uneven number of 'heading', 'description' and"
            " 'amount' items\nThere should be an equal number of each of"
            " these items"
        )


def _convert_checkbox_items(
    response: Iterable[dict],
) -> tuple[list[dict], set[str]]:
    field_ids = {
        item["field_id"]
        for item in response
        if item["field_type"] == "checkboxesField"
    }
    items_to_process = (i for i in response if i["field_id"] in field_ids)

    text_items = []
    for item in items_to_process:
        text_item = _build_item(
            item["question"],
            item["field_id"],
            "question_heading",
        )

        if len(item.get("answer", [])) == 0:  # if no checkboxes are selected
            text_item["presentation_type"] = "text"
            text_item["answer"] = "None selected."
            text_items.append(text_item)
            continue

        text_items.append(text_item)
        text_items.extend(
            {
                "question": remove_dashes_underscores_capitalize(answer),
                "field_type": item.get("field_type"),
                "field_id": item["field_id"],
                "answer": "Yes",
                "presentation_type": "text",
            }
            for answer in item["answer"]
        )

    return text_items, field_ids


def _flatten_field_ids(field_id):
    field_ids = []
    if isinstance(field_id, (tuple, list)):
        field_ids.append(tuple(field_id))
        for fid in field_id:
            field_ids.append(fid)
    else:
        field_ids.append(field_id)
    return field_ids


def _convert_non_number_grouped_fields(
    response: Iterable[dict],
) -> tuple[list[dict], set[str]]:
    items_to_process = [
        item
        for item in response
        if item["presentation_type"] == "grouped_fields"
        and item["field_type"]
        != "numberField"  # we ignore number fields as they are handled separately # noqa
    ]

    text_items = []
    for item in items_to_process:
        if "answer" not in item or len(item.get("answer", [])) == 0:
            text_items.append(
                _build_item(item["question"][0], item["field_id"])
            )
            continue

        for question_answer_tuple, field_id in zip(
            item["answer"], item["field_id"]
        ):
            question, answer = question_answer_tuple
            text_items.append(
                {
                    "question": question,
                    "field_type": item.get("field_type"),
                    "field_id": field_id,
                    "answer": answer,
                    "presentation_type": "text",
                }
            )

    processed_field_ids = set()
    for item in items_to_process:
        processed_field_ids.update(_flatten_field_ids(item["field_id"]))

    return text_items, processed_field_ids


def _make_field_ids_hashable(item: dict) -> dict:
    field_id = item["field_id"]
    if isinstance(field_id, list):
        item["field_id"] = tuple(field_id)
    return item


def create_ui_components(
    response_with_some_unhashable_fields: list[dict], applicaition_id: str
) -> List[ApplicatorsResponseComponent]:
    response = list(
        map(_make_field_ids_hashable, response_with_some_unhashable_fields)
    )

    grouped_fields_items, gfi_field_ids = _convert_heading_description_amount(
        response
    )
    text_items_from_checkbox, tifc_field_ids = _convert_checkbox_items(
        response
    )
    (
        text_items_from_grouped_fields,
        tifgf_field_ids,
    ) = _convert_non_number_grouped_fields(response)

    processed_field_ids = gfi_field_ids | tifc_field_ids | tifgf_field_ids
    unprocessed_items = [
        i for i in response if i["field_id"] not in processed_field_ids
    ]
    post_processed_items = (
        grouped_fields_items
        + text_items_from_checkbox
        + text_items_from_grouped_fields
        + unprocessed_items
    )

    field_ids_in_order = []
    for i in response:
        field_ids_in_order.extend(_flatten_field_ids(i["field_id"]))

    # we need to preserve the order of the fields from the back-end,
    # so we re-sort it here
    post_processed_items.sort(
        key=lambda x: field_ids_in_order.index(x["field_id"])
    )

    return (_ui_component_from_factory(item, applicaition_id) for item in post_processed_items)
