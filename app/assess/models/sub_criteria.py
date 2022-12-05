import inspect
from dataclasses import dataclass
from app.assess.models.theme import Theme


@dataclass
class SubCriteria:
    id: str
    name: str
    score_submitted: bool
    themes: list[Theme]

    @classmethod
    def from_filtered_dict(cls, d: dict):
        # Filter unknown fields from JSON dictionary
        return cls(
            **{
                k: v
                for k, v in d.items()
                if k in inspect.signature(cls).parameters
            }
        )
