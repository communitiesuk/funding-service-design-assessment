from typing import List
from .application import Application
from datetime import datetime
from slugify import slugify


class Round(object):

    def __init__(
            self,
            opens: datetime,
            deadline: datetime,
            identifier: str = None,
            applications: List[Application] = None
    ):
        self._identifier = identifier
        self.opens = opens
        self.deadline = deadline
        self.applications = applications

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
            identifier=str(data.get("round_identifier"))
        )

    def add_application(self, application: Application):
        if not self.applications:
            self.applications = []
        self.applications.append(application)
