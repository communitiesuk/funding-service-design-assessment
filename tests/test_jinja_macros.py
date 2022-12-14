import re

from app.assess.models.ui.assessor_task_list import _CriteriaSubCriteria
from app.assess.models.ui.assessor_task_list import _SubCriteria
from flask import get_template_attribute
from flask import render_template_string


class TestJinjaMacros(object):
    def test_criteria_macro(self, request_ctx):
        rendered_html = render_template_string(
            "{{criteria_element(sub_criterias, name, name_classes,"
            " total_criteria_score, total_criteria_score_possible,"
            " weighting)}}",
            criteria_element=get_template_attribute(
                "macros/criteria_element.html", "criteria_element"
            ),
            sub_criterias=[
                _CriteriaSubCriteria(
                    id="1",
                    name="Sub Criteria 1",
                    status="Not started",
                    theme_count=1,
                    score=2,
                ),
                _CriteriaSubCriteria(
                    id="2",
                    name="Sub Criteria 2",
                    status="Not started",
                    theme_count=2,
                    score=2,
                ),
            ],
            name="Example title",
            name_classes="example-class",
            total_criteria_score=0,
            total_criteria_score_possible=0,
            weighting=0.5,
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

    def test_section_macro(self, request_ctx):
        rendered_html = render_template_string(
            "{{section_element(name, sub_criterias)}}",
            section_element=get_template_attribute(
                "macros/section_element.html", "section_element"
            ),
            name="Example title",
            sub_criterias=[
                _SubCriteria(id="1", name="Sub Criteria 1"),
                _SubCriteria(id="2", name="Sub Criteria 2"),
            ],
        )

        # replacing new lines to more easily regex match the html
        rendered_html = rendered_html.replace("\n", "")

        assert re.search(
            r"<h2.*\S*Example title\S*</h2>", rendered_html
        ), "Title not found"

        assert (
            len(re.findall(r"<table.*?</table>", rendered_html)) == 1
        ), "Should have 1 table"

        assert (
            len(
                re.findall(
                    r"<caption.*?This section is not scored\. Can be used for"
                    r" due diligence checks\.*?</caption>",
                    rendered_html,
                )
            )
            == 1
        ), "Should have 1 caption"

        assert (
            len(re.findall(r"<thead.*?</thead>", rendered_html)) == 1
        ), "Should have 1 table header"
        assert (
            len(re.findall(r"<tbody.*?</tbody>", rendered_html)) == 1
        ), "Should have 1 table body"

    def test_score_macro(self, request_ctx):
        rendered_html = render_template_string(
            "{{scores(score_form_name, score_list, score_error)}}",
            scores=get_template_attribute("macros/scores.html", "scores"),
            score_form_name="Score",
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

    def test_justification_macro(self, request_ctx):
        rendered_html = render_template_string(
            "{{justification(justification_form_name, justification_error)}}",
            justification=get_template_attribute(
                "macros/justification.html", "justification"
            ),
            justification_form_name="Justification",
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
