"""
Tests if known pages of the website contain expected content
"""
import pytest
from config import Config
from flask import url_for
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.errorhandler import NoSuchElementException
from tests.route_testing_conf import intro_routes_and_test_content
from tests.utils import print_html_page


@pytest.mark.usefixtures("selenium_chrome_driver")
@pytest.mark.usefixtures("live_server")
@pytest.mark.usefixtures("client_class")
class TestContentWithChrome:
    def route_content_test(self, route_rel: str, content_dict: dict):
        url = url_for("default_bp.index", _external=True) + route_rel[1:]
        self.driver.get(url=url)
        source = self.driver.page_source
        print_html_page(
            html=source,
            service_dict={
                "name": Config.LOCAL_SERVICE_NAME,
                "host": "",
            },
            route_rel=route_rel,
        )
        for content_item in content_dict:
            print(f"Testing {route_rel}")
            error_message = ""
            tag = content_item.get("tag")
            name = content_item.get("name")
            contains = content_item.get("contains")
            found_element = None
            if name:
                try:
                    found_element = self.driver.find_element(By.NAME, name)
                except NoSuchElementException:
                    error_message = (
                        "Element name '" + name + "' was not found in " + url
                    )
                assert found_element is not None, error_message
                if contains and type(contains) == str:
                    text = found_element.text
                    error_message = (
                        "Element name '"
                        + name
                        + "' does not contain "
                        + contains
                    )
                    assert contains == text, error_message
            elif tag and contains:
                try:
                    found_element = self.driver.find_element(
                        By.XPATH,
                        "//" + tag + "[contains(text(), '" + contains + "')]",
                    )
                except NoSuchElementException:
                    error_message = (
                        "Element tag '"
                        + tag
                        + "' with content '"
                        + contains
                        + "' was not found in "
                        + url
                    )
                assert found_element is not None, error_message

    def test_intro_routes_content(self, client):
        """
        GIVEN Our Flask Application is running
        WHEN dictionary of known routes is requested (GET)
        THEN check that each page returned conforms to WCAG standards
        """
        for route_rel, content_dict in intro_routes_and_test_content.items():
            self.route_content_test(route_rel, content_dict)


# TODO reinstate this with correct values once design finalised
# def test_assessment_form_routes_content(self, client):
#     """
#     GIVEN Our Flask Application is running
#     WHEN dictionary of known routes is requested (GET)
#     THEN check that each page returned conforms to WCAG standards
#     """
#     for route_rel, content_dict in assessment_form_test_routes().items():
#         self.route_content_test(route_rel, content_dict)
