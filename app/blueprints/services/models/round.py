import inspect
from dataclasses import dataclass
from typing import List

from .application import Application


@dataclass
class Round:
    id: str
    assessment_deadline: str
    deadline: str
    fund_id: str
    opens: str
    title: str
    short_name: str
    guidance_url: str = ""
    all_uploaded_documents_section_available: bool = False
    application_fields_download_available: bool = False
    display_logo_on_pdf_exports: bool = False
    applications: List[Application] = None

    @classmethod
    def from_dict(cls, d: dict):
        # Filter unknown fields from JSON dictionary
        return cls(
            **{
                k: v
                for k, v in d.items()
                if k in inspect.signature(cls).parameters
            }
        )

    @staticmethod
    def from_json(data: dict):
        return Round(
            title=data.get("title"),
            id=data.get("id"),
            fund_id=data.get("fund_id"),
            opens=data.get("opens"),
            deadline=data.get("deadline"),
            guidance_url=data.get("guidance_url"),
            all_uploaded_documents_section_available=data.get(
                "all_uploaded_documents_section_available"
            )
            or False,
            application_fields_download_available=data.get(
                "application_fields_download_available"
            )
            or False,
            display_logo_on_pdf_exports=data.get("display_logo_on_pdf_exports")
            or False,
        )

    def add_application(self, application: Application):
        if not self.applications:
            self.applications = []
        self.applications.append(application)

    def add_eligibility_criteria(self, key: str, value: object):
        self.eligibility_criteria.update({key: value})
