import inspect
from dataclasses import dataclass


@dataclass
class Tag:
    id: str
    value: str
    user: str
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
