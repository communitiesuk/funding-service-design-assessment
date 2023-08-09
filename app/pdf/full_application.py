from dataclasses import dataclass
from functools import partial

from app.pdf.pdf_generator import _generate_pdf


@dataclass
class QuestionAndAnswer:
    question: str
    answer: str
    number: str


@dataclass
class Section:
    number: str
    title: str
    questions_and_answers: list[QuestionAndAnswer]


@dataclass
class FullApplicationPdfContext:
    title: str
    response_id: str
    submission_to: str
    submitted_on: str
    organisation_name: str
    organisation_shortname: str
    organisation_logo_uri: str
    sections: list[Section]

    @classmethod
    def from_data(cls, args):
        sections = [
            Section(
                number="",
                title=args.form_name_to_title_map.get(section),
                questions_and_answers=[
                    QuestionAndAnswer(question=q, answer=a, number="")
                    for q, a in q_and_a.items()
                ],
            )
            for section, q_and_a in args.question_to_answer.items()
        ]

        if args.round.all_uploaded_documents_section_available:
            sections.insert(
                0,
                Section(
                    number="",
                    title="All uploaded documents",
                    questions_and_answers=[
                        QuestionAndAnswer(
                            question=i["question"],
                            answer=i.get("answer"),
                            number="",
                        )
                        for i in args.all_uploaded_documents
                    ],
                ),
            )

        return cls(
            title=args.fund.name,
            response_id=args.application_json["short_id"],
            submission_to=f"{args.fund.name} {args.round.title}",
            submitted_on=args.application_json["date_submitted"],
            organisation_name=args.fund.owner_organisation_name,
            organisation_shortname=args.fund.owner_organisation_shortname,
            organisation_logo_uri=args.fund.owner_organisation_logo_uri
            if args.round.display_logo_on_pdf_exports
            else None,
            sections=sections,
        )


generate_full_application_pdf = partial(
    _generate_pdf, "app/pdf/templates/full_application.html"
)
