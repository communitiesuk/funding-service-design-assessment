from dataclasses import asdict
from typing import NamedTuple

from app.assess.helpers import generate_csv_of_application
from app.assess.models.fund import Fund
from app.assess.models.round import Round
from app.pdf.full_application import FullApplicationPdfContext
from app.pdf.full_application import generate_full_application_pdf
from flask import abort
from flask import send_file
from fsd_utils import generate_text_of_application


class ApplicationFileRepresentationArgs(NamedTuple):
    fund: Fund
    round: Round
    short_id: str
    form_name_to_title_map: dict
    question_to_answer: dict
    application_json: dict
    all_uploaded_documents: list[dict]


def _generate_text_of_application(args: ApplicationFileRepresentationArgs):
    from app.assess.routes import download_file

    text = generate_text_of_application(
        args.question_to_answer, args.fund.name
    )
    return download_file(text, "text/plain", f"{args.short_id}_answers.txt")


def _generate_csv_of_application(args: ApplicationFileRepresentationArgs):
    from app.assess.routes import download_file

    csv = generate_csv_of_application(
        args.question_to_answer, args.fund, args.application_json
    )
    return download_file(csv, "text/csv", f"{args.short_id}_answers.csv")


def _generate_pdf_of_application(args: ApplicationFileRepresentationArgs):
    context = FullApplicationPdfContext.from_data(args)
    if pdf_file := generate_full_application_pdf(asdict(context)):
        pdf_file.seek(0)
        return send_file(
            pdf_file,
            download_name=f"{args.short_id}_answers.pdf",
            as_attachment=True,
        )


_FILE_GENERATORS = {
    "txt": _generate_text_of_application,
    "csv": _generate_csv_of_application,
    "pdf": _generate_pdf_of_application,
}


def generate_file_content(
    args: ApplicationFileRepresentationArgs, file_type: str
):
    if file_generator := _FILE_GENERATORS.get(file_type):
        return file_generator(args)

    abort(404)
