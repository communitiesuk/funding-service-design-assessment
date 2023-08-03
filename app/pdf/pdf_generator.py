from io import BytesIO
from typing import Dict

from flask import current_app
from jinja2 import Environment
from jinja2 import FileSystemLoader
from xhtml2pdf import pisa


class PDFGenerator:
    def __init__(self, template_path: str) -> None:
        self.template_path = template_path

    def _render_template(self, context: Dict[str, str]) -> str:
        env = Environment(loader=FileSystemLoader("."))
        template = env.get_template(self.template_path)
        return template.render(context)

    def generate_pdf(self, context: Dict[str, str]) -> BytesIO:
        pdf_file = BytesIO()
        html_content = self._render_template(context)
        convert_html_to_pdf(html_content, pdf_file)
        return pdf_file


def convert_html_to_pdf(html_content: str, pdf_file: BytesIO) -> bool:
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
    if pisa_status.err:
        current_app.logger.error(
            f"Error while converting HTML to PDF: {str(pisa_status.err)}"
        )
        return False
    return True
