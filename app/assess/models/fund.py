from dataclasses import dataclass
from typing import List

from app.assess.models.round import Round


@dataclass
class Fund:
    name: str
    id: str
    description: str
    short_name: str
    rounds: List[Round] = None

    @staticmethod
    def from_json(data: dict):
        return Fund(
            name=data.get("name"),
            id=data.get("id"),
            description=data.get("description"),
            short_name=data.get("short_name"),
        )

    def add_round(self, fund_round: Round):
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)
