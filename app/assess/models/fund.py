from typing import List
from .round import Round
from slugify import slugify


class Fund(object):

    def __init__(
        self,
        name: str,
        identifier: str = None,
        rounds: List[Round] = None,
    ):
        self.name = name
        self.rounds = rounds
        self._identifier = identifier

    @property
    def identifier(self):
        if self._identifier:
            return self._identifier
        return slugify(self.name)

    @identifier.setter
    def identifier(self, value):
        self._identifier = value

    @identifier.deleter
    def identifier(self):
        del self._identifier

    @staticmethod
    def from_json(data: dict):
        return Fund(
            name=data.get("name"),
            identifier=data.get("identifier")
        )

    def add_round(self, fund_round: Round):
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)
