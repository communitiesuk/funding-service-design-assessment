import re

import pytest
from app.assess.forms.comments_form import CommentsForm
from app.assess.forms.scores_and_justifications import ScoreForm
from app.assess.models.ui.applicants_response import AboveQuestionAnswerPair
from app.assess.models.ui.applicants_response import (
    AboveQuestionAnswerPairHref,
)
from app.assess.models.ui.applicants_response import BesideQuestionAnswerPair
from app.assess.models.ui.applicants_response import (
    BesideQuestionAnswerPairHref,
)
from app.assess.models.ui.applicants_response import (
    FormattedBesideQuestionAnswerPair,
)
from app.assess.models.ui.applicants_response import MonetaryKeyValues
from app.assess.models.ui.applicants_response import (
    QuestionAboveHrefAnswerList,
)
from app.assess.models.ui.applicants_response import QuestionHeading
from app.assess.models.ui.assessor_task_list import _Criteria
from app.assess.models.ui.assessor_task_list import _CriteriaSubCriteria
from app.assess.models.ui.assessor_task_list import _SubCriteria
from app.assess.views.filters import format_address
from bs4 import BeautifulSoup
from flask import g
from flask import get_template_attribute
from flask import render_template_string
from flask_wtf.csrf import generate_csrf
from fsd_utils.authentication.models import User


class TestJinjaMacros(object):
    def test_criteria_macro_lead_assessor(self, request_ctx):
        g.user = User(
            full_name="Test Lead Assessor",
            email="test@example.com",
            roles=["LEAD_ASSESSOR", "ASSESSOR", "COMMENTER"],
            highest_role="LEAD_ASSESSOR",
        )
        rendered_html = render_template_string(
            "{{criteria_element(criteria, name_classes, application_id)}}",
            criteria_element=get_template_attribute(
                "macros/criteria_element.html", "criteria_element"
            ),
            criteria=_Criteria(
                name="Example title",
                total_criteria_score=0,
                total_criteria_score_possible=0,
                weighting=0.5,
                sub_criterias=[
                    _CriteriaSubCriteria(
                        id="1",
                        name="Sub Criteria 1",
                        status="NOT_STARTED",
                        theme_count=1,
                        score=2,
                    ),
                    _CriteriaSubCriteria(
                        id="2",
                        name="Sub Criteria 2",
                        status="NOT_STARTED",
                        theme_count=2,
                        score=2,
                    ),
                ],
            ),
            name_classes="example-class",
            application_id=1,
            g=g,
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        assert (
            soup.find("h3", class_="example-class").text == "Example title"
        ), "Title not found"

        assert (
            soup.find(
                "p", class_="govuk-body govuk-!-margin-bottom-2"
            ).text.strip()
            == "50% of overall score."
        ), "Weighting not found"

        table = soup.find(
            "table",
            class_=(
                "govuk-table govuk-!-margin-bottom-6"
                " govuk-table-no-bottom-border"
            ),
        )
        assert table is not None, "Table should have border negation class"
        assert len(soup.find_all("table")) == 1, "Should have 1 table"
        assert len(table.find_all("thead")) == 1, "Should have 1 table header"
        assert len(table.find_all("tbody")) == 1, "Should have 1 table body"
        assert len(table.find_all("tr")) == 4, "Should have 4 table rows"

        assert (
            table.find("strong", text="Total criteria score") is not None
        ), "Should have Total criteria score"
        assert (
            table.find("th", text="Score out of 5") is not None
        ), "Should have Score out of 5 column"

    def test_criteria_macro_commenter(self, request_ctx):
        g.user = User(
            full_name="Test Commenter",
            email="test@example.com",
            roles=["COMMENTER"],
            highest_role="COMMENTER",
        )

        rendered_html = render_template_string(
            "{{criteria_element(criteria, name_classes, application_id)}}",
            criteria_element=get_template_attribute(
                "macros/criteria_element.html", "criteria_element"
            ),
            criteria=_Criteria(
                name="Example title",
                total_criteria_score=0,
                total_criteria_score_possible=0,
                weighting=0.5,
                sub_criterias=[
                    _CriteriaSubCriteria(
                        id="1",
                        name="Sub Criteria 1",
                        status="NOT_STARTED",
                        theme_count=1,
                        score=2,
                    ),
                    _CriteriaSubCriteria(
                        id="2",
                        name="Sub Criteria 2",
                        status="NOT_STARTED",
                        theme_count=2,
                        score=2,
                    ),
                ],
            ),
            name_classes="example-class",
            application_id=1,
            g=g,
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        assert len(soup.select("tr")) == 3, "Should have 3 table rows"

        assert not soup.find(
            "strong", text="Total criteria score"
        ), "Should not have Total criteria score"

        assert not soup.find(
            "th", text="Score out of 5"
        ), "Should not have Score out of 5 column"

    def test_section_macro(self, request_ctx):
        rendered_html = render_template_string(
            "{{section_element(name, sub_criterias, application_id)}}",
            section_element=get_template_attribute(
                "macros/section_element.html", "section_element"
            ),
            name="Example title",
            sub_criterias=[
                _SubCriteria(
                    id="1",
                    name="Sub Criteria 1",
                ),
                _SubCriteria(
                    id="2",
                    name="Sub Criteria 2",
                ),
            ],
            application_id=1,
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        assert soup.find(
            "h2",
            {"class": "govuk-heading-l govuk-!-margin-top-4"},
            text="Example title",
        ), "Title not found"

    def test_score_macro(self, request_ctx):
        form = ScoreForm()
        form.score.errors = True
        rendered_html = render_template_string(
            "{{scores(form, score_list)}}",
            scores=get_template_attribute("macros/scores.html", "scores"),
            form=form,
            score_list=[
                (5, "Strong"),
                (4, "Good"),
                (3, "Satisfactory"),
                (2, "Partial"),
                (1, "Poor"),
            ],
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        assert (
            soup.find("p", {"class": "govuk-body"}).text.strip()
            == "Select a score from the list:"
        ), "Title not found"

        radios = soup.find_all("div", {"class": "govuk-radios__item"})
        assert len(radios) == 5, "Should have 5 radios"

        score_spans = soup.find_all(
            "span", {"class": "govuk-!-font-weight-bold"}
        )
        assert len(score_spans) == 5, "Should have 5 score values for radios"

    def test_comment_macro(self, request_ctx):
        rendered_html = render_template_string(
            "{{comment_box(comment_form)}}",
            comment_box=get_template_attribute(
                "macros/comments_box.html", "comment_box"
            ),
            comment_form=CommentsForm(),
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        add_comment_label = soup.find("label")
        assert add_comment_label.text.strip() == "Add a comment"
        assert add_comment_label is not None, "Add Comment label not found"

        save_comment_button = soup.find("button")
        assert save_comment_button.text.strip() == "Save comment"
        assert save_comment_button is not None, "Save comment button not found"

    def test_justification_macro(self, request_ctx):
        form = ScoreForm()
        form.justification.errors = True
        rendered_html = render_template_string(
            "{{justification(form)}}",
            justification=get_template_attribute(
                "macros/justification.html", "justification"
            ),
            form=form,
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        title_label = soup.find("label")
        assert title_label.text.strip() == "Add rationale for this score"
        assert title_label is not None, "Title not found"

        error_message = soup.find("p", class_="govuk-error-message")
        assert (
            error_message.text.strip()
            == "Error: Please provide rationale for this score"
        )
        assert error_message is not None, "Intentional error not found"

    def test_monetary_key_values(self, request_ctx):
        meta = MonetaryKeyValues.from_dict(
            {
                "question": ("Test Caption", "Test Description"),
                "answer": [("Question 1", "50.00"), ("Question 2", "100.00")],
            }
        )

        rendered_html = render_template_string(
            "{{ monetary_key_values(meta) }}",
            monetary_key_values=get_template_attribute(
                "macros/theme/monetary_key_values.jinja2",
                "monetary_key_values",
            ),
            meta=meta,
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        assert soup.find("caption", text="Test Caption"), "Caption not found"
        assert soup.find(
            "th", text="Test Description"
        ), "Column description not found"
        assert soup.find("td", text="£50.00"), "First answer not found"
        assert soup.find("td", text="£100.00"), "Second answer not found"
        assert soup.find("td", text="Total"), "Total header not found"
        assert soup.find("td", text="£150.00"), "Total not found"

    @pytest.mark.parametrize(
        "clazz, macro_name, answer, expected",
        [
            (
                AboveQuestionAnswerPair,
                "question_above_answer",
                50.00,
                "£50.00",
            ),
            (
                BesideQuestionAnswerPair,
                "question_beside_answer",
                "Test Answer",
                "Test Answer",
            ),
        ],
    )
    def test_question_above_answer(
        self, request_ctx, clazz, macro_name, answer, expected
    ):
        meta = clazz.from_dict({"question": "Test Question", "answer": answer})

        rendered_html = render_template_string(
            f"{{{{ {macro_name}(meta) }}}}",
            **{
                macro_name: get_template_attribute(
                    f"macros/theme/{macro_name}.jinja2", macro_name
                )
            },
            meta=meta,
        )

        assert "Test Question" in rendered_html, "Question not found"
        assert expected in rendered_html, "Answer not found"

    @pytest.mark.parametrize(
        "clazz, macro_name",
        [
            (AboveQuestionAnswerPairHref, "question_above_href_answer"),
            (BesideQuestionAnswerPairHref, "question_beside_href_answer"),
        ],
    )
    def test_question_above_href_answer(self, request_ctx, clazz, macro_name):
        meta = clazz.from_dict(
            {"question": "Test Question", "answer": "Test Answer"},
            href="http://www.example.com",
        )

        rendered_html = render_template_string(
            f"{{{{ {macro_name}(meta) }}}}",
            **{
                macro_name: get_template_attribute(
                    f"macros/theme/{macro_name}.jinja2", macro_name
                )
            },
            meta=meta,
        )

        assert "Test Question" in rendered_html, "Question not found"
        assert "Test Answer" in rendered_html, "Answer not found"
        assert "http://www.example.com" in rendered_html, "Link href not found"

    def test_question_above_href_answer_list(self, request_ctx):
        meta = QuestionAboveHrefAnswerList.from_dict(
            {"question": "Test Question"},
            key_to_url_dict={
                "File 1": "http://example.com/file1.pdf",
                "File 2": "http://example.com/file2.pdf",
            },
        )

        rendered_html = render_template_string(
            "{{ question_above_href_answer_list(meta) }}",
            question_above_href_answer_list=get_template_attribute(
                "macros/theme/question_above_href_answer_list.jinja2",
                "question_above_href_answer_list",
            ),
            meta=meta,
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        assert "Test Question" in rendered_html, "Question not found"
        assert (
            soup.find("a", href="http://example.com/file1.pdf").text
            == "File 1"
        ), "File 1 not found"
        assert (
            soup.find("a", href="http://example.com/file2.pdf").text
            == "File 2"
        ), "File 2 not found"
        assert not soup.find(text="Not provided."), "Unexpected 'Not provided."

    def test_question_beside_with_formatted_answer_multiline(
        self, request_ctx
    ):
        meta = FormattedBesideQuestionAnswerPair.from_dict(
            {
                "question": "Test Question",
                "answer": (
                    "Test Address, null, Test Town Or City, null, QQ12 7QQ"
                ),
            },
            formatter=format_address,
        )

        rendered_html = render_template_string(
            "{{ question_beside_with_formatted_answer(meta) }}",
            question_beside_with_formatted_answer=get_template_attribute(
                "macros/theme/question_beside_with_formatted_answer.jinja2",
                "question_beside_with_formatted_answer",
            ),
            meta=meta,
        )

        assert "Test Question" in rendered_html, "Answer not found"
        assert (
            "Test Address<br>" in rendered_html
        ), "First line of address not found"
        assert (
            "Test Town Or City<br>" in rendered_html
        ), "Second line of address not found"
        assert "QQ12 7QQ" in rendered_html, "Third line of address not found"

    @pytest.mark.parametrize(
        "clazz, arguments, expected_unique_id",
        [
            (
                MonetaryKeyValues,
                {
                    "data": {
                        "question": ("Test Caption", "unique-key-1"),
                        "answer": [
                            ("Question 1", "50.00"),
                            ("Question 2", "100.00"),
                        ],
                    }
                },
                "unique-key-1",
            ),
            (
                AboveQuestionAnswerPair,
                {"data": {"question": "unique-key-2", "answer": 50.00}},
                "unique-key-2",
            ),
            (
                BesideQuestionAnswerPair,
                {
                    "data": {
                        "question": "unique-key-3",
                        "answer": "Test Answer",
                    }
                },
                "unique-key-3",
            ),
            (
                AboveQuestionAnswerPairHref,
                {
                    "data": {
                        "question": "unique-key-4",
                        "answer": "Test Answer",
                    },
                    "href": "http://www.example.com",
                },
                "unique-key-4",
            ),
            (
                BesideQuestionAnswerPairHref,
                {
                    "data": {
                        "question": "unique-key-5",
                        "answer": "Test Answer",
                    },
                    "href": "http://www.example.com",
                },
                "unique-key-5",
            ),
            (
                FormattedBesideQuestionAnswerPair,
                {
                    "data": {
                        "question": "unique-key-6",
                        "answer": (
                            "Test Address, null, Test Town Or City, null,"
                            " QQ12 7QQ"
                        ),
                    },
                    "formatter": format_address,
                },
                "unique-key-6",
            ),
            (
                QuestionHeading,
                {
                    "data": {
                        "question": "unique-key-7",
                    }
                },
                "unique-key-7",
            ),
        ],
    )
    def test_theme_mapping_works_based_on_meta_key(
        self, request_ctx, clazz, arguments, expected_unique_id
    ):
        meta = clazz.from_dict(**arguments)

        rendered_html = render_template_string(
            "{{ theme([meta]) }}",
            theme=get_template_attribute("macros/theme.html", "theme"),
            meta=meta,
        )

        assert expected_unique_id in rendered_html, "Unique ID not found"

    def test_banner_summary_macro(self, request_ctx):
        fund_name = "Test Fund"
        project_reference = "TEST123"
        project_name = "Test Project"
        funding_amount_requested = 123456.78
        workflow_status = "SUBMITTED"
        assessment_flag = None

        rendered_html = render_template_string(
            "{{ banner_summary(fund_name, project_reference, project_name,"
            " funding_amount_requested, workflow_status, flag) }}",
            banner_summary=get_template_attribute(
                "macros/banner_summary.html", "banner_summary"
            ),
            fund_name=fund_name,
            project_reference=project_reference,
            project_name=project_name,
            funding_amount_requested=funding_amount_requested,
            workflow_status=workflow_status,
            flag=assessment_flag,
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        assert (
            soup.find("h1", class_="fsd-banner-content").text.strip()
            == "Fund: Test Fund"
        ), "Fund name not found"
        assert (
            soup.find("h2", class_="fsd-banner-content").text.strip()
            == "Project reference: TEST123"
        ), "Project reference not found"
        assert soup.find(
            "h3",
            class_="fsd-banner-content",
            text="Project name: Test Project",
        ), "Project name not found"
        assert soup.find(
            "h3",
            class_="fsd-banner-content",
            text="Total funding requested: £123,456.78",
        ), "Funding amount not found"
        assert soup.find(
            "h3", class_="fsd-banner-content", text="Submitted"
        ), "Workflow status not found"

    def test_stopped_flag_macro(self, request_ctx):
        fund_name = "Test Fund"
        project_reference = "TEST123"
        project_name = "Test Project"
        funding_amount_requested = 123456.78
        display_status = "STOPPED"
        assessment_flag = {
            "flag_type": {"name": "STOPPED"},
            "justification": "Test justification",
            "sections_to_flag": ["Test section"],
            "date_created": "2020-01-01 12:00:00",
        }

        rendered_html = render_template_string(
            "{{ banner_summary(fund_name, project_reference, project_name,"
            " funding_amount_requested, display_status, flag) }}",
            banner_summary=get_template_attribute(
                "macros/banner_summary.html", "banner_summary"
            ),
            fund_name=fund_name,
            project_reference=project_reference,
            project_name=project_name,
            funding_amount_requested=funding_amount_requested,
            display_status=display_status,
            flag=assessment_flag,
        )

        assert "Stopped" in rendered_html

    def test_flag_application_button(self, request_ctx):
        rendered_html = render_template_string(
            "{{flag_application_button(12345)}}",
            flag_application_button=get_template_attribute(
                "macros/flag_application_button.html",
                "flag_application_button",
            ),
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        flag_container = soup.find(
            "div", {"class": "govuk-grid-row govuk-!-text-align-right"}
        )
        assert (
            flag_container is not None
        ), "Flag application button container not found"

        flag_link = flag_container.find(
            "a",
            {
                "href": "/assess/flag/12345",
                "class": "govuk-button primary-button",
                "data-module": "govuk-button",
            },
        )
        assert flag_link is not None, "Flag application button not found"
        assert (
            flag_link.text.strip() == "Flag application"
        ), "Flag application button text does not match"

    def test_mark_qa_complete_button(self, request_ctx):
        rendered_html = render_template_string(
            "{{mark_qa_complete_button(12345)}}",
            mark_qa_complete_button=get_template_attribute(
                "macros/mark_qa_complete_button.html",
                "mark_qa_complete_button",
            ),
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        button_container = soup.find(
            "div", class_="govuk-grid-row govuk-!-text-align-right"
        )
        assert (
            button_container is not None
        ), "Mark QA complete button container not found"

        button_element = button_container.find(
            "a", href="/assess/qa_complete/12345"
        )
        assert button_element is not None, "Mark QA complete button not found"

    def test_stopped_assessment_flag(self, request_ctx):
        rendered_html = render_template_string(
            "{{assessment_stopped(flag, user_info)}}",
            assessment_stopped=get_template_attribute(
                "macros/assessment_flag.html", "assessment_stopped"
            ),
            flag={
                "flag_type": {"name": "STOPPED"},
                "justification": "Test justification",
                "sections_to_flag": ["Test section"],
                "date_created": "2020-01-01 12:00:00",
            },
            user_info={
                "full_name": "Test user",
                "highest_role": "Test role",
                "email_address": "test@example.com",
            },
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        alert_div = soup.find("div", class_="assessment-alert")

        assert (
            alert_div.find(
                "h1", class_="assessment-alert__heading govuk-heading-l"
            ).text
            == "Assessment Stopped"
        ), "Flag type not found"

        assert (
            alert_div.find("h2", class_="govuk-heading-m").text == "Reason"
        ), "Reason heading not found"

        assert (
            alert_div.find("p", class_="govuk-body").text
            == "Test justification"
        ), "Justification not found"

        user_paragraph = alert_div.find("p", class_="govuk-body-s")
        assert (
            "test@example.com" in user_paragraph.text
        ), "User email not found"

        assert "Test role" in user_paragraph.text, "User role not found"

        date_created_paragraph = alert_div.find("p", class_="govuk-body-s")
        assert (
            date_created_paragraph is not None
        ), "Date created paragraph not found"

    def test_assessment_flag(self, request_ctx):
        def get_section_from_sub_criteria_id(self, sub_criteria_id):
            return {
                "sub_section_name": sub_criteria_id,
                "parent_section_name": "Parent Test section",
            }

        rendered_html = render_template_string(
            "{{assessment_flagged(state, flag, user_info, state)}}",
            assessment_flagged=get_template_attribute(
                "macros/assessment_flag.html", "assessment_flagged"
            ),
            state=type(
                "State",
                (),
                {
                    "get_section_from_sub_criteria_id": get_section_from_sub_criteria_id
                },
            )(),
            flag={
                "flag_type": {"name": "Test flag"},
                "justification": "Test justification",
                "sections_to_flag": ["Test section"],
                "date_created": "2020-01-01 12:00:00",
            },
            user_info={
                "full_name": "Test user",
                "highest_role": "Test role",
                "email_address": "test@example.com",
            },
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        alert_div = soup.find("div", class_="assessment-alert--flagged")

        reason_heading = alert_div.find("h2", text="Reason")
        assert reason_heading is not None, "Reason heading not found"
        justification = reason_heading.find_next_sibling(
            "p", class_="govuk-body"
        )
        assert (
            justification is not None
            and justification.text == "Test justification"
        ), "Justification not found"

        section_heading = alert_div.find("h2", text="Section(s) flagged")
        assert (
            section_heading is not None
        ), "Section(s) flagged heading not found"
        section = section_heading.find_next_sibling("p", class_="govuk-body")
        assert (
            section is not None
            and section.text
            == "Test section (Parent Test section) (Opens in new tab)"
        ), "Section not found"

        user_info = alert_div.find_all("p", class_="govuk-body-s")
        assert any(
            "test@example.com" in info.text for info in user_info
        ), "User info not found"

        date_created = alert_div.find(
            "p", class_="govuk-body-s"
        ).find_next_sibling("p", class_="govuk-body-s")
        assert date_created is not None and re.match(
            r"\d{2}/\d{2}/\d{4} at \d{2}:\d{2}", date_created.text
        ), "Date created not found"

    def test_assessment_completion_state_completed(self, request_ctx):
        rendered_html = render_template_string(
            "{{assessment_complete(state, flag, csrf_token, application_id,"
            " current_user_role)}}",
            assessment_complete=get_template_attribute(
                "macros/assessment_completion.html", "assessment_complete"
            ),
            state=type("State", (), {"workflow_status": "COMPLETED"})(),
            flag=None,
            csrf_token=generate_csrf(),
            application_id=1,
            current_user_role="LEAD_ASSESSOR",
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        assert (
            soup.find("h2", class_="assessment-alert__heading").string
            == "Assessment complete"
        )

        assert (
            soup.find("p", class_="govuk-body").string
            == "You have marked this assessment as complete."
        )

    def test_assessment_completion_flagged(self, request_ctx):
        rendered_html = render_template_string(
            "{{assessment_complete(state, flag, csrf_token, application_id,"
            " current_user_role)}}",
            assessment_complete=get_template_attribute(
                "macros/assessment_completion.html", "assessment_complete"
            ),
            state=type("State", (), {"workflow_status": "IN_PROGRESS"})(),
            flag=type(
                "Flag",
                (),
                {"flag_type": type("FlagType", (), {"name": "RESOLVED"})},
            )(),
            csrf_token=generate_csrf(),
            application_id=1,
            current_user_role="LEAD_ASSESSOR",
        )

        soup = BeautifulSoup(rendered_html, "html.parser")

        assert (
            soup.find("h2", class_="assessment-alert__heading").string
            == "All sections assessed"
        )
