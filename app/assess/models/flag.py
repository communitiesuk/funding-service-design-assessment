import inspect
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class FlagType(Enum):
    FLAGGED = 0
    STOPPED = 1
    QA_COMPLETED = 2
    RESOLVED = 3


@dataclass()
class Flag:
    id: str
    justification: str
    sections_to_flag: str
    flag_type: FlagType | str
    application_id: str
    date_created: str
    user_id: str
    is_qa_complete: bool = False

    def __post_init__(self):
        if self.flag_type:
            self.flag_type = FlagType[self.flag_type]
        self.date_created = datetime.fromisoformat(self.date_created).strftime(
            "%Y-%m-%d %X"
        )

    @classmethod
    def from_dict(cls, d: dict):
        # Filter unknown fields from JSON dictionary
        return cls(
            **{
                k: v
                for k, v in d.items()
                if k in inspect.signature(cls).parameters
            }
        )


@dataclass()
class Flags:
    id: str
    justification: str
    sections_to_flag: str
    flag_type: FlagType | str
    application_id: str
    date_created: str
    user_id: str
    is_qa_complete: bool = False

    def __post_init__(self):
        if self.flag_type:
            self.flag_type = FlagType[self.flag_type]
        self.date_created = datetime.fromisoformat(self.date_created).strftime(
            "%Y-%m-%d %X"
        )

    @classmethod
    def from_dict(cls, lst: list):
        all_flags = [
            cls(
                **{
                    k: v
                    for k, v in d.items()
                    if k in inspect.signature(cls).parameters
                }
            )
            for d in lst
        ]

        print(f"ALL FLAGS MOCK:::{all_flags}")
        return all_flags
