import inspect
from dataclasses import dataclass


@dataclass
class Comment:
    comment: str
    user_id: str
    date_created: str
    email_address: str
    full_name: str
    highest_role: str
    theme_id: str
    fund_short_name: str

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

    @property
    def from_lead_assessor(self):
        return (
            f"{self.fund_short_name}_{self.highest_role}"
            == f"{self.fund_short_name}_LEAD_ASSESSOR"
        )

    @property
    def from_assessor(self):
        return (
            f"{self.fund_short_name}_{self.highest_role}"
            == f"{self.fund_short_name}_ASSESSOR"
        )

    @property
    def from_any_assessor(self):
        return self.from_lead_assessor or self.from_assessor
