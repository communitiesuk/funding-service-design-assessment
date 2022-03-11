from dataclasses import dataclass
from typing import List

from app.assess.models.round import Round
from slugify import slugify


@dataclass
class Fund:
    name: str
    _identifier: str = None
    rounds: List[Round] = None

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
            name=data.get("fund_name"), _identifier=data.get("fund_id")
        )

    def add_round(self, fund_round: Round):
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)
