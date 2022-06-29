from dataclasses import dataclass
import re
from typing import Dict, List


def remove_currency_symbols(currency_str):

    return re.sub("[,$£]", "", currency_str)

@dataclass
class TotalMoneyTableView:

    total : int
    table_elements: List[Dict[str, int]]
    prefix: str = "£"

    @classmethod
    def from_question_json(cls, question_json):

        table_elements = {"rows": []}

        table_elements["rows"] = [
            [
                {"text": field["title"]},
                {"text": field["answer"], "format": "numeric"},
            ]
            for field in question_json["fields"]
        ]

        total = sum(
            [
                int(remove_currency_symbols(field["answer"]))
                for field in question_json["fields"]
            ]
        )

        return TotalMoneyTableView(total, table_elements=table_elements)

    def row_dict(self):

        return { "rows" : [*self.table_elements["rows"], [{"text": "Total"}, {"text": f"{self.prefix}{self.total}", "format": "numeric"}]] }
