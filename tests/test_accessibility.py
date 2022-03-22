"""
Tests if selected pages of the website are accessible when rendered,
according to WCAG standards
"""
import os

import pytest
from app.config import LOCAL_SERVICE_NAME
from axe_selenium_python import Axe
from json2html import json2html
from selenium.webdriver.chrome.webdriver import WebDriver
from tests.route_testing_conf import assessment_form_test_routes
from tests.route_testing_conf import intro_routes_and_test_content
from tests.utils import get_service
from tests.utils import get_service_html_filepath


def get_report_heading(service_dict: dict, route_rel: str):
    service = get_service(service_dict)
    heading = (
        "<p>Testing service: "
        + str(service["name"])
        + " at: "
        + str(service["host"])
        + "<h1>Axe Violations Report for route /"
        + route_rel
        + "</h1>"
    )
    return heading


def get_report_filename(service_dict: dict, route_rel: str, route_name: str):
    service = get_service(service_dict)
    report_root = ""

    if service["name"] != LOCAL_SERVICE_NAME:
        report_root = service["name"] + "__"

    if not route_name:
        if route_rel:
            route_name = route_rel.replace("/", "_")
        else:
            route_name = "index"

    return report_root + route_name


def print_axe_report(results: dict, service_dict: dict, route_rel: str):
    """
    Prints an html report from aXe generated results
    """
    results_html = json2html.convert(
        json=results["violations"],
        table_attributes=(
            "border='1' cellpadding='10' cellspacing='0' bordercolor='black'"
        ),
    )
    heading = get_report_heading(service_dict, route_rel)
    results_with_title = heading + results_html
    html_basename, filename = get_service_html_filepath(
        "axe_reports", service_dict, route_rel
    )

    os.makedirs(html_basename, exist_ok=True)
    f = open(html_basename + filename, "w")
    f.write(results_with_title)
    f.close()


@pytest.mark.usefixtures("selenium_chrome_driver")
@pytest.mark.usefixtures("live_server")
def run_axe_and_print_report(
    driver: WebDriver,
    service_dict: dict = None,
    route_rel: str = "",
):
    """
    Generates an html report from aXe generate has generated a report
    :return A json report
    """
    service = get_service(service_dict)
    if route_rel and route_rel[0] != "/":
        route_rel = "/" + route_rel
    route = service["host"] + route_rel
    driver.get(route)
    axe = Axe(driver)
    axe.inject()
    results = axe.run()
    print_axe_report(results, service_dict, route_rel)

    return results


@pytest.mark.app(debug=False)
def test_app(app):
    assert not app.debug, "Ensure the app not in debug mode"


@pytest.mark.usefixtures("selenium_chrome_driver")
@pytest.mark.usefixtures("live_server")
class TestAccessibilityWithChrome:
    def test_homepage_accessible(self):
        """
        GIVEN Our Flask Application is running
        WHEN the '/' page (index) is requested (GET)
        THEN check that page returned conforms to WCAG standards
        """
        route_rel = ""
        results = run_axe_and_print_report(
            driver=self.driver, route_rel=str(route_rel)
        )
        assert len(results["violations"]) <= 1
        assert (
            len(results["violations"]) == 0
            or results["violations"][0]["impact"] == "minor"
        )

    def test_intro_routes_accessible(self):
        """
        GIVEN Our Flask Application is running
        WHEN dictionary of known routes is requested (GET)
        THEN check that each page returned conforms to WCAG standards
        """
        for route_rel, _ in intro_routes_and_test_content.items():
            results = run_axe_and_print_report(
                driver=self.driver, route_rel=str(route_rel)
            )
            assert len(results["violations"]) <= 1
            assert (
                len(results["violations"]) == 0
                or results["violations"][0]["impact"] == "minor"
            )

    def test_assessment_form_routes_accessible(self):
        """
        GIVEN Our Flask Application is running
        WHEN dictionary of known routes is requested (GET)
        THEN check that each page returned conforms to WCAG standards
        """
        for route_rel, _ in assessment_form_test_routes().items():
            results = run_axe_and_print_report(
                driver=self.driver, route_rel=str(route_rel)
            )
            assert len(results["violations"]) <= 1
            assert (
                len(results["violations"]) == 0
                or results["violations"][0]["impact"] == "minor"
            )

    def test_unknown_page_returns_accessible_404(self):
        """
        GIVEN Our Flask Application is running
        WHEN the '/page-that-does-not-exist' page is requested (GET)
        THEN check that a 404 page that is returned conforms to WCAG standards
        """
        route_rel = "page-does-not-exist"
        results = run_axe_and_print_report(
            driver=self.driver, route_rel=str(route_rel)
        )

        assert len(results["violations"]) <= 2
        assert (
            len(results["violations"]) == 0
            or results["violations"][0]["impact"] == "minor"
        )
