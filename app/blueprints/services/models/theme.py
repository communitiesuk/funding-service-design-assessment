import inspect
from dataclasses import dataclass

from app.blueprints.services.models.answer import Answer


@dataclass
class Theme:
    id: str
    name: str
    answers: list[Answer]

    @classmethod
    def from_filtered_dict(cls, d: dict):
        # Filter unknown fields from JSON dictionary
        return cls(
            **{k: v for k, v in d.items() if k in inspect.signature(cls).parameters}
        )
