"""
Tests if known pages of the website contain expected content
"""
import os

import pytest
from tests.utils import print_html_page
from tests.route_testing_conf import known_routes_and_test_content
from app.config import LOCAL_SERVICE_NAME
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.errorhandler import NoSuchElementException
from flask import url_for


@pytest.mark.usefixtures("selenium_chrome_driver")
@pytest.mark.usefixtures("live_server")
@pytest.mark.usefixtures("client_class")
class TestContentWithChrome:

    def test_known_routes_content(self, client):
        """
        GIVEN Our Flask Application is running
        WHEN dictionary of known routes is requested (GET)
        THEN check that each page returned conforms to WCAG standards
        """
        for route_rel, content_dict in known_routes_and_test_content.items():
            url = url_for("default_bp.index", _external=True) + route_rel[1:]
            self.driver.get(url=url)
            source = self.driver.page_source
            testing = client.application.config.get("FLASK_ENV")
            print_html_page(
                html=str(testing)+source,
                service_dict={
                    "name": LOCAL_SERVICE_NAME,
                    "host": "",
                },
                route_rel=route_rel,
            )
            for content_item in content_dict:
                error_message = ""
                tag = content_item.get("tag")
                name = content_item.get("name")
                contains = content_item.get("contains")
                found_element = None
                if name:
                    try:
                        found_element = self.driver.find_element(
                            By.NAME, name
                        )
                    except NoSuchElementException:
                        error_message = (
                            "Element name '"
                            + name
                            + "' was not found in "
                            + url
                        )
                    assert found_element is not None, error_message
                elif tag and contains:
                    try:
                        found_element = self.driver.find_element(
                            By.XPATH, "//"+tag+"[contains(text(), '"+contains+"')]"
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
