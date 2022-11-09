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
    eligibility_criteria: dict
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
        eligibility_criteria = {}
        if "eligibility_criteria" in data:
            for key, value in data["eligibility_criteria"].items():
                eligibility_criteria.update({key: value})
        return Round(
            title=data.get("title"),
            id=data.get("id"),
            fund_id=data.get("fund_id"),
            opens=data.get("opens"),
            deadline=data.get("deadline"),
            eligibility_criteria=eligibility_criteria,
        )

    def add_application(self, application: Application):
        if not self.applications:
            self.applications = []
        self.applications.append(application)

    def add_eligibility_criteria(self, key: str, value: object):
        self.eligibility_criteria.update({key: value})
