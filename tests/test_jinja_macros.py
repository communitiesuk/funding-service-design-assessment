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
from app.assess.models.ui.applicants_response import QuestionHeading
from app.assess.models.ui.assessor_task_list import _Criteria
from app.assess.models.ui.assessor_task_list import _CriteriaSubCriteria
from app.assess.models.ui.assessor_task_list import _SubCriteria
from app.assess.views.filters import format_address
from flask import g
from flask import get_template_attribute
from flask import render_template_string
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

        # replacing new lines to more easily regex match the html
        rendered_html = rendered_html.replace("\n", "")

        assert re.search(
            r'<h3 class="example-class">\S*Example title\S*</h3>',
            rendered_html,
        ), "Title not found"

        assert re.search(
            r"<p.*50%.*of overall score.*?</p>", rendered_html
        ), "Weighting not found"

        assert re.findall(
            r"<table.*govuk-table-no-bottom-border.*?</table>", rendered_html
        ), "Table should have border negation class"

        assert (
            len(re.findall(r"<table.*?</table>", rendered_html)) == 1
        ), "Should have 1 table"
        assert (
            len(re.findall(r"<thead.*?</thead>", rendered_html)) == 1
        ), "Should have 1 table header"
        assert (
            len(re.findall(r"<tbody.*?</tbody>", rendered_html)) == 1
        ), "Should have 1 table body"

        assert (
            len(re.findall(r"<tr.*?</tr>", rendered_html)) == 4
        ), "Should have 4 table rows"

        assert re.search(
            r"<strong>Total criteria score</strong>", rendered_html
        ), "Should have Total criteria score"
        assert re.search(
            r"<th.*Score out of 5.*?</th>", rendered_html
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

        # replacing new lines to more easily regex match the html
        rendered_html = rendered_html.replace("\n", "")
        assert (
            len(re.findall(r"<tr.*?</tr>", rendered_html)) == 3
        ), "Should have 3 table rows"
        assert (
            re.search(r"<strong>Total criteria score</strong>", rendered_html)
            is None
        ), "Should not have Total criteria score"
        assert (
            re.search(r"<th.*Score out of 5.*?</th>", rendered_html) is None
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

        # replacing new lines to more easily regex match the html
        rendered_html = rendered_html.replace("\n", "")

        assert re.search(
            r"<h2.*\S*Example title\S*</h2>", rendered_html
        ), "Title not found"

        assert (
            len(re.findall(r"<table.*?</table>", rendered_html)) == 0
        ), "Should have 1 table"

        assert (
            len(re.findall(r"<thead.*?</thead>", rendered_html)) == 0
        ), "Should have 1 table header"
        assert (
            len(re.findall(r"<tbody.*?</tbody>", rendered_html)) == 0
        ), "Should have 1 table body"

    def test_score_macro(self, request_ctx):
        rendered_html = render_template_string(
            "{{scores(form, score_list, score_error)}}",
            scores=get_template_attribute("macros/scores.html", "scores"),
            form=ScoreForm(),
            score_list=[
                (5, "Strong"),
                (4, "Good"),
                (3, "Satisfactory"),
                (2, "Partial"),
                (1, "Poor"),
            ],
            score_error=False,
        )

        # replacing new lines to more easily regex match the html
        rendered_html = rendered_html.replace("\n", "")

        assert re.search(
            r"<p.*\S*Select a score from the list:\S*</p>", rendered_html
        ), "Title not found"

        assert (
            len(
                re.findall(
                    r"""<div class="govuk-radios__item">""", rendered_html
                )
            )
            == 5
        ), "Should have 5 radios"

        assert (
            len(re.findall(r"""<span.*?\S*\d</span>""", rendered_html)) == 5
        ), "Should have 5 score values for radios"

    def test_comment_macro(self, request_ctx):
        rendered_html = render_template_string(
            "{{comment_box(comment_form)}}",
            comment_box=get_template_attribute(
                "macros/comments_box.html", "comment_box"
            ),
            comment_form=CommentsForm(),
        )

        # replacing new lines to more easily regex match the html
        rendered_html = rendered_html.replace("\n", "")

        assert re.search(
            r"Add a comment</label>", rendered_html
        ), "Add Comment label not found"

        assert re.search(
            r"Save comment</button>", rendered_html
        ), "Save comment button not found"

    def test_justification_macro(self, request_ctx):
        rendered_html = render_template_string(
            "{{justification(form, justification_error)}}",
            justification=get_template_attribute(
                "macros/justification.html", "justification"
            ),
            form=ScoreForm(),
            justification_error=True,
        )

        # replacing new lines to more easily regex match the html
        rendered_html = rendered_html.replace("\n", "")

        assert re.search(
            r"<label.*\S*Add rationale for this \s* score</label>",
            rendered_html,
        ), "Title not found"

        assert re.search(
            r"<p.*Please provide rationale for this score\s*</p>",
            rendered_html,
        ), "Intentional error not found"

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

        assert re.search(
            r"<caption.*\S*Test Caption\S*</caption>", rendered_html
        ), "Caption not found"

        assert re.search(
            r"<th.*\S*Test Description\S*</th>", rendered_html
        ), "Column description not found"

        assert re.search(
            r"<td.*\S*>£50.00</td>", rendered_html
        ), "First answer not found"

        assert re.search(
            r"<td.*\S*>£100.00</td>", rendered_html
        ), "Second answer not found"

        assert re.search(
            r"<td.*\S*Total\S*</td>", rendered_html
        ), "Total header not found"

        assert re.search(
            r"<td.*\S*>£150.00</td>", rendered_html
        ), "Total not found"

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
            "{{ theme('a-theme-id', [meta]) }}",
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

        # Replace newlines for easier regex matching
        rendered_html = rendered_html.replace("\n", "")

        assert re.search(
            r"Fund: Test Fund",
            rendered_html,
        ), "Fund name not found"
        assert re.search(
            r"Project\s+reference: TEST123",
            rendered_html,
        ), "Project reference not found"
        assert re.search(
            r"Project\s+name: Test Project",
            rendered_html,
        ), "Project name not found"
        assert re.search(
            r"Total funding requested:\s+&pound;123,456.78",
            rendered_html,
        ), "Funding amount not found"
        assert re.search(
            r"Submitted",
            rendered_html,
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
            "section_to_flag": "Test section",
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

        assert re.search(
            r"Stopped", rendered_html
        ), "Stopped text not found in banner"

    def test_flag_application_button(self, request_ctx):
        rendered_html = render_template_string(
            "{{flag_application_button(12345)}}",
            flag_application_button=get_template_attribute(
                "macros/flag_application_button.html",
                "flag_application_button",
            ),
        )

        rendered_html = rendered_html.replace("\n", "")

        assert re.search(
            r'<div class="govuk-grid-row govuk-!-text-align-right">.*</div>',
            rendered_html,
        ), "Flag application button container not found"
        assert re.search(
            r'<a href="/assess/flag/12345".*Flag application.*</a>',
            rendered_html,
        ), "Flag application button not found"

    def test_mark_qa_complete_button(self, request_ctx):
        rendered_html = render_template_string(
            "{{mark_qa_complete_button(12345)}}",
            mark_qa_complete_button=get_template_attribute(
                "macros/mark_qa_complete_button.html",
                "mark_qa_complete_button",
            ),
        )

        rendered_html = rendered_html.replace("\n", "")

        assert re.search(
            r'<div class="govuk-grid-row govuk-!-text-align-right">.*</div>',
            rendered_html,
        ), "Mark QA complete button container not found"
        assert re.search(
            r'<a href="/assess/qa_complete/12345".*Mark QA complete.*</a>',
            rendered_html,
        ), "Mark QA complete button not found"

    def test_stopped_assessment_flag(self, request_ctx):
        rendered_html = render_template_string(
            "{{assessment_stopped(flag, user_info)}}",
            assessment_stopped=get_template_attribute(
                "macros/assessment_flag.html", "assessment_stopped"
            ),
            flag={
                "flag_type": {"name": "STOPPED"},
                "justification": "Test justification",
                "section_to_flag": "Test section",
                "date_created": "2020-01-01 12:00:00",
            },
            user_info={
                "full_name": "Test user",
                "highest_role": "Test role",
                "email_address": "test@example.com",
            },
        )

        # replacing new lines to more easily regex match the html
        rendered_html = rendered_html.replace("\n", "")

        assert re.search(
            r"Assessment Stopped",
            rendered_html,
        ), "Flag type not found"

        assert re.search(
            r"Reason",
            rendered_html,
        ), "Reason heading not found"

        assert re.search(
            r"Test justification",
            rendered_html,
        ), "Justification not found"

        assert re.search(
            r"Test user.*\S*Test role.*\S*test@example.com",
            rendered_html,
        ), "User info not found"

        assert re.search(
            r"\d{2}/\d{2}/\d{4} at \d{2}:\d{2}",
            rendered_html,
        ), "Date created not found"

    def test_assessment_flag(self, request_ctx):
        rendered_html = render_template_string(
            "{{assessment_flagged(flag, user_info)}}",
            assessment_flagged=get_template_attribute(
                "macros/assessment_flag.html", "assessment_flagged"
            ),
            flag={
                "flag_type": {"name": "Test flag"},
                "justification": "Test justification",
                "section_to_flag": "Test section",
                "date_created": "2020-01-01 12:00:00",
            },
            user_info={
                "full_name": "Test user",
                "highest_role": "Test role",
                "email_address": "test@example.com",
            },
        )

        # replacing new lines to more easily regex match the html
        rendered_html = rendered_html.replace("\n", "")

        assert re.search(
            r"Test Flag",
            rendered_html,
        ), "Flag type not found"

        assert re.search(
            r"Reason",
            rendered_html,
        ), "Reason heading not found"

        assert re.search(
            r"Test justification",
            rendered_html,
        ), "Justification not found"

        assert re.search(
            r"Section flagged",
            rendered_html,
        ), "Section flagged heading not found"

        assert re.search(
            r"Test section",
            rendered_html,
        ), "Section not found"

        assert re.search(
            r"Test user.*\S*Test role.*\S*test@example.com",
            rendered_html,
        ), "User info not found"

        assert re.search(
            r"\d{2}/\d{2}/\d{4} at \d{2}:\d{2}",
            rendered_html,
        ), "Date created not found"
