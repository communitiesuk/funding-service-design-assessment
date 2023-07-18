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
    all_uploaded_documents_section_available: bool
    guidance_url: str = ""
    rounds: List[Round] = field(default_factory=list)

    @staticmethod
    def from_json(data: dict):
        return Fund(
            name=data.get("name"),
            id=data.get("id"),
            description=data.get("description"),
            short_name=data.get("short_name"),
            guidance_url=data.get("guidance_url"),
            all_uploaded_documents_section_available=data.get(
                "all_uploaded_documents_section_available"
            )
            or False,
        )

    def add_round(self, fund_round: Round):
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)
