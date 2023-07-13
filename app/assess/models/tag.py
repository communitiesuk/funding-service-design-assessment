import inspect
from dataclasses import dataclass


@dataclass
class Tag:
    id: str
    value: str
    creator_user_id: str
    active: bool
    colour: str

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            **{
                k: v
                for k, v in d.items()
                if k in inspect.signature(cls).parameters
            }
        )


@dataclass
class AssociatedTag:
    application_id: str
    tag_id: str
    value: str
    user_id: str
    associated: bool
    colour: str

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            **{
                k: v
                for k, v in d.items()
                if k in inspect.signature(cls).parameters
            }
        )
