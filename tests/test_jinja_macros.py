import re

from flask import get_template_attribute
from flask import render_template_string


class TestJinjaMacros(object):
    def test_scored_section_macro(self, request_ctx):
        rendered_html = render_template_string(
            "{{scoredSection(config)}}",
            scoredSection=get_template_attribute(
                "macros/scored_section.html", "scoredSection"
            ),
            config={
                "title": "Example title",
                "title_classes": "example-class",
                "weighting": 0.5,
                "total_criteria_score": 0,
                "total_criteria_score_possible": 0,
                "sub_criteria_rows": [
                    {
                        "href": "/example/href/1",
                        "name": "Example name 1",
                        "theme_count": 1,
                        "score": 1,
                        "status": "Not started",
                    },
                    {
                        "href": "/example/href/2",
                        "name": "Example name 2",
                        "theme_count": 2,
                        "score": 2,
                        "status": "Not started",
                    },
                ],
            },
        )

        # replacing new lines to more easily regex match the html
        rendered_html = rendered_html.replace("\n", "")

        assert re.search(
            r'<h3 class="example-class">\s+Example title</h3>', rendered_html
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

        assert (
            len(re.findall("govuk-tag--blue", rendered_html)) == 2
        ), "Should have 2 blue tags"
        assert (
            len(re.findall(r'href="/example/href/\d', rendered_html)) == 2
        ), "Should have 2 blue tags"

    def test_unscored_section_macro(self, request_ctx):
        rendered_html = render_template_string(
            "{{unscoredSection(config)}}",
            unscoredSection=get_template_attribute(
                "macros/unscored_section.html", "unscoredSection"
            ),
            config={
                "title": "Example title",
                "rows": [
                    {
                        "href": "/section/1",
                        "name": "Example name 1",
                    },
                    {
                        "href": "/section/1",
                        "name": "Example name 1",
                    },
                ],
            },
        )

        # replacing new lines to more easily regex match the html
        rendered_html = rendered_html.replace("\n", "")

        assert re.search(
            r"<h2.*?Example title.*?</h2>", rendered_html
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
