from dataclasses import dataclass
from datetime import datetime
from typing import List

from slugify import slugify

from .application import Application


@dataclass
class Round:
    opens: datetime
    deadline: datetime
    _identifier: str = None
    applications: List[Application] = None

    @property
    def identifier(self):
        if self._identifier:
            return self._identifier
        return slugify(self.deadline)

    @identifier.setter
    def identifier(self, value):
        self._identifier = value

    @identifier.deleter
    def identifier(self):
        del self._identifier

    @staticmethod
    def from_json(data: dict):
        return Round(
            opens=data.get("opens"),
            deadline=data.get("deadline"),
            _identifier=str(data.get("round_identifier")),
        )

    def add_application(self, application: Application):
        if not self.applications:
            self.applications = []
        self.applications.append(application)
