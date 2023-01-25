import inspect
from dataclasses import dataclass
from typing import List

from .application import Application


@dataclass
class Round:
    id: str
    assessment_criteria_weighting: list
    assessment_deadline: str
    deadline: str
    fund_id: str
    opens: str
    title: str
    short_name: str
    applications: List[Application] = None

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

    @staticmethod
    def from_json(data: dict):
        return Round(
            title=data.get("title"),
            id=data.get("id"),
            fund_id=data.get("fund_id"),
            opens=data.get("opens"),
            deadline=data.get("deadline"),
        )

    def add_application(self, application: Application):
        if not self.applications:
            self.applications = []
        self.applications.append(application)

    def add_eligibility_criteria(self, key: str, value: object):
        self.eligibility_criteria.update({key: value})
