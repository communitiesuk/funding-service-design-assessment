from io import BytesIO

from flask import current_app
from jinja2 import Environment
from jinja2 import FileSystemLoader
from xhtml2pdf import pisa


def _render_template(template_path: str, context) -> str:
    env = Environment(loader=FileSystemLoader("."))
    template = env.get_template(template_path)
    return template.render(context)


def _generate_pdf(template_path: str, context) -> BytesIO:
    pdf_file = BytesIO()
    html_content = _render_template(template_path, context)
    _convert_html_to_pdf(html_content, pdf_file)
    return pdf_file


def _convert_html_to_pdf(html_content: str, pdf_file: BytesIO) -> bool:
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
    if pisa_status.err:
        current_app.logger.error(
            f"Error while converting HTML to PDF: {str(pisa_status.err)}"
        )
        return False
    return True
