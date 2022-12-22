import inspect
from dataclasses import dataclass

@dataclass
class Comment:
    comment: str
    user_id: str
    date_created: str
    email_address: str
    full_name:str
    highest_role:str
    theme_id:str

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