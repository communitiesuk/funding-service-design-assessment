from config import Config
from tests.conftest import create_valid_token
from tests.conftest import test_assessor_claims
from tests.conftest import test_commenter_claims
from tests.conftest import test_lead_assessor_claims
from tests.conftest import test_roleless_user_claims


class TestAuthorisation:
    def test_any_unauthorised_route_redirects_to_home(self, flask_test_client):
        """
        GIVEN an unauthorised user
        WHEN the user tries to access any route
        THEN tne user is redirected to the "/" root
        Args:
            flask_test_client:

        Returns:

        """
        # Set cookie to none
        flask_test_client.set_cookie("localhost", "fsd_user_token", "")
        response = flask_test_client.get("/any-route")

        assert response.status_code == 302
        assert response.location == "/"

    def test_any_unauthorised_visit_to_root_prompts_user_to_sign_in(
        self, flask_test_client
    ):
        """
        GIVEN an unauthorised user
        WHEN the user visits the homepage "/"
        THEN tne user is prompted to sign in
        Args:
            flask_test_client:

        Returns:

        """
        # Set cookie to none
        flask_test_client.set_cookie("localhost", "fsd_user_token", "")
        response = flask_test_client.get("/")
        assert response.status_code == 200
        assert b"Please sign in to continue." in response.data
        assert (
            b'<a href="authenticator/sso/login" role="button"'
            b' draggable="false" class="govuk-button"'
            b' data-module="govuk-button">'
            in response.data
        )

    def test_roleless_user_redirected_to_roles_error(self, flask_test_client):
        """
        GIVEN an authorised user with no roles
        WHEN the user tries to access any route
        THEN tne user is redirected to the authenticator roles error page
        Args:
            flask_test_client:

        Returns:

        """
        flask_test_client.set_cookie(
            "localhost",
            "fsd_user_token",
            create_valid_token(test_roleless_user_claims),
        )
        response = flask_test_client.get("/any-route")

        assert response.status_code == 302
        assert (
            response.location
            == "https://authenticator/service/user?roles_required=COMMENTER"
        )

    def test_authorised_lead_assessor_redirected_to_dashboard(
        self, flask_test_client
    ):
        """
        GIVEN an authorised user
        WHEN the user tries to access the service "/" root
        THEN tne user is redirected to their dashboard
        Args:
            flask_test_client:

        Returns:

        """
        flask_test_client.set_cookie(
            "localhost",
            "fsd_user_token",
            create_valid_token(test_lead_assessor_claims),
        )
        response = flask_test_client.get("/")

        assert response.status_code == 302
        assert response.location == Config.DASHBOARD_ROUTE

        response = flask_test_client.get("/", follow_redirects=True)
        assert response.status_code == 200
        assert (
            b'<h1 class="govuk-heading-xl fsd-banner-content">Team'
            b" dashboard</h1>"
            in response.data
        )
        assert b'<div class="lead-dashboard-stats">' in response.data

    def test_authorised_assessor_redirected_to_dashboard(
        self, flask_test_client
    ):
        """
        GIVEN an authorised user
        WHEN the user tries to access the service "/" root
        THEN tne user is redirected to their dashboard
        Args:
            flask_test_client:

        Returns:

        """
        flask_test_client.set_cookie(
            "localhost",
            "fsd_user_token",
            create_valid_token(test_assessor_claims),
        )
        response = flask_test_client.get("/")

        assert response.status_code == 302
        assert response.location == Config.DASHBOARD_ROUTE

        response = flask_test_client.get("/", follow_redirects=True)
        assert response.status_code == 200
        assert (
            b'<h1 class="govuk-heading-xl fsd-banner-content">Team'
            b" dashboard</h1>"
            in response.data
        )
        assert b'<div class="lead-dashboard-stats">' not in response.data

    def test_authorised_commenter_redirected_to_dashboard(
        self, flask_test_client
    ):
        """
        GIVEN an authorised user
        WHEN the user tries to access the service "/" root
        THEN tne user is redirected to their dashboard
        Args:
            flask_test_client:

        Returns:

        """
        flask_test_client.set_cookie(
            "localhost",
            "fsd_user_token",
            create_valid_token(test_commenter_claims),
        )
        response = flask_test_client.get("/")

        assert response.status_code == 302
        assert response.location == Config.DASHBOARD_ROUTE

        response = flask_test_client.get("/", follow_redirects=True)
        assert response.status_code == 200
        assert (
            b'<h1 class="govuk-heading-xl fsd-banner-content">Team'
            b" dashboard</h1>"
            in response.data
        )
        assert b'<div class="lead-dashboard-stats">' not in response.data
