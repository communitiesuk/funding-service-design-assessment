from dataclasses import dataclass
from typing import Dict
from typing import List
from typing import Union


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
    funding_amount_requested: str
    project_reference: str
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
            funding_amount_requested=json.get("funding_amount_requested"),
            project_reference=json.get("project_reference"),
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

    def get_sub_sections_metadata(self) -> List[Dict]:
        """This function returns metadata for all sub-sections in a given section.

        Return
        -------
        sub_sections_list Eg,. [{"sub_section_name": "Funding breakdown",
                                "sub_section_id": "funding_breakdown",
                                "parent_section_name": "Managment case",
                                "section_type": "Scored",
                                },...]

        """
        sub_sections_list = []

        # Loop through each section and its sub-criterias, and append the metadata to the list.
        for section in self.sections:
            for sub_section in section.sub_criterias:
                sub_sections_list.append(
                    {
                        "sub_section_name": sub_section.name,
                        "sub_section_id": sub_section.id,
                        "parent_section_name": section.name,
                        "section_type": section.name,
                    }
                )

        # Loop through each criteria and its sub-criterias, and append the metadata to the list.
        for criteria in self.criterias:
            for sub_section in criteria.sub_criterias:
                sub_sections_list.append(
                    {
                        "sub_section_name": sub_section.name,
                        "sub_section_id": sub_section.id,
                        "parent_section_name": criteria.name,
                        "section_type": "Scored",
                    }
                )

        # Return the final metadata list for sub-sections.
        return sub_sections_list

    def get_section_from_sub_criteria_id(
        self, sub_criteria_id: str
    ) -> Union[None, Dict]:
        """Retrieve metadata for a specific sub-section using its unique identifier.

        Return
        -------
        sub_section_metadata  Eg., {"sub_section_name": "Funding breakdown",
                                    "sub_section_id": "funding_breakdown",
                                    "parent_section_name": "Managment case",
                                    "section_type": "Scored",
                                    }
        """

        # Get all metadata for all sub-sections.
        sub_sections_metadata = self.get_sub_sections_metadata()

        # Loop through each item in the metadata list to find the sub-section with the given id.
        for item in sub_sections_metadata:
            if sub_criteria_id == item["sub_section_id"]:
                return item

        return None
