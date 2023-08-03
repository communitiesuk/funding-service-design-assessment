from app.pdf.pdf_generator import PDFGenerator


def test_generate_pdf():
    context = {
        "title": "Test PDF",
        "heading": "Hello, Test!",
        "content": "This is a test PDF generated using Jinja and XHTML2PDF.",
        "items": ["Item 1", "Item 2", "Item 3"],
    }

    bytes = PDFGenerator("tests/pdf/test_pdf_template.html").generate_pdf(
        context
    )
    assert bytes is not None
    # todo(tferns): add a pdf reading library and assert on the contents.


def test_generate_full_application_pdf():
    context = {
        "title": "Community Ownership Fund",
        "response_id": "ANON-VUAR-U4HM-V",
        "submission_to": "Community Ownership Fund Round 2",
        "submitted_on": "2022-08-19 11:58:37",
        "sections": [
            {
                "number": "1.1",
                "title": "Title",
                "questions_and_answers": [
                    {"question": "Question 1", "answer": "Answer 1"},
                    {"question": "Question 2", "answer": "Answer 2"},
                ],
            }
        ],
    }

    bytes = PDFGenerator(
        "app/pdf/templates/full_application.html"
    ).generate_pdf(context)
    breakpoint()  # <- remove this, just for testing.
    # todo(tferns): add a pdf reading library and assert on the contents.
    assert bytes is not None
