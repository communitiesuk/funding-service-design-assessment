from dataclasses import dataclass
from typing import List


@dataclass
class _SubCriteria:
    id: str
    name: str


@dataclass
class _Section:
    name: str
    sub_criterias: List[_SubCriteria]


@dataclass
class _CriteriaSubCriteria(_SubCriteria):
    status: str
    score: int
    theme_count: int


@dataclass
class _Criteria:
    name: str
    total_criteria_score: int
    total_criteria_score_possible: int
    weighting: float
    sub_criterias: List[_CriteriaSubCriteria]


@dataclass
class AssessorTaskList:
    fund_name: str
    project_name: str
    short_id: str
    workflow_status: str
    date_submitted: str
    sections: List[_Section]
    criterias: List[_Criteria]

    @classmethod
    def from_json(cls, json: dict):
        return AssessorTaskList(
            fund_name=json.get("fund_name"),
            short_id=json.get("short_id"),
            project_name=json.get("project_name"),
            date_submitted=json.get("date_submitted"),
            workflow_status=json.get("workflow_status"),
            sections=[
                _Section(
                    name=section["name"],
                    sub_criterias=[
                        _SubCriteria(
                            id=sub_criteria["id"],
                            name=sub_criteria["name"],
                        )
                        for sub_criteria in section["sub_criterias"]
                    ],
                )
                for section in json["sections"]
            ],
            criterias=[
                _Criteria(
                    name=criteria["name"],
                    total_criteria_score=criteria["total_criteria_score"],
                    total_criteria_score_possible=criteria[
                        "total_criteria_score_possible"
                    ],
                    weighting=criteria["weighting"],
                    sub_criterias=[
                        _CriteriaSubCriteria(
                            id=sub_criteria["id"],
                            name=sub_criteria["name"],
                            status=sub_criteria["status"],
                            score=sub_criteria["score"],
                            theme_count=sub_criteria["theme_count"],
                        )
                        for sub_criteria in criteria["sub_criterias"]
                    ],
                )
                for criteria in json["criterias"]
            ],
        )
