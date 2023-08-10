from dataclasses import dataclass
from dataclasses import field
from typing import List

from app.assess.models.round import Round


@dataclass
class Fund:
    name: str
    id: str
    description: str
    short_name: str
    guidance_url: str = ""
    owner_organisation_name: str = ""
    owner_organisation_shortname: str = ""
    owner_organisation_logo_uri: str = ""
    rounds: List[Round] = field(default_factory=list)

    @staticmethod
    def from_json(data: dict):
        return Fund(
            name=data.get("name"),
            id=data.get("id"),
            description=data.get("description"),
            short_name=data.get("short_name"),
            guidance_url=data.get("guidance_url"),
            owner_organisation_name=data.get("owner_organisation_name"),
            owner_organisation_shortname=data.get(
                "owner_organisation_shortname"
            ),
            owner_organisation_logo_uri=data.get(
                "owner_organisation_logo_uri"
            ),
        )

    def add_round(self, fund_round: Round):
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)
