import pytest
from config import Config
from tests.conftest import create_invalid_token
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
        THEN the user is redirected to the "/" root
        Args:
            flask_test_client:

        Returns:

        """
        # Set user auth cookie to none
        flask_test_client.set_cookie("localhost", "fsd_user_token", "")
        response = flask_test_client.get("/any-route")

        assert response.status_code == 302
        assert response.location == "/"

    def test_any_invalid_token_route_redirects_to_home(
        self, flask_test_client
    ):
        """
        GIVEN an unauthorised user
        WHEN the user tries to access any route
        THEN the user is redirected to the "/" root
        Args:
            flask_test_client:

        Returns:

        """
        # Set user auth cookie to invalid token
        flask_test_client.set_cookie(
            "localhost",
            "fsd_user_token",
            create_invalid_token(),
        )
        response = flask_test_client.get("/any-route")

        assert response.status_code == 302
        assert response.location == "/"

    def test_any_unauthorised_visit_to_root_prompts_user_to_sign_in(
        self, flask_test_client
    ):
        """
        GIVEN an unauthorised user
        WHEN the user visits the homepage "/"
        THEN the user is prompted to sign in
        Args:
            flask_test_client:

        Returns:

        """
        # Set user auth cookie to none
        flask_test_client.set_cookie("localhost", "fsd_user_token", "")
        response = flask_test_client.get("/")
        assert response.status_code == 200
        assert b"Please sign in to continue." in response.data
        assert (
            b'<a href="https://authenticator/sso/login" role="button"'
            b' draggable="false" class="govuk-button"'
            b' data-module="govuk-button">'
            in response.data
        )

    def test_roleless_user_redirected_to_roles_error(self, flask_test_client):
        """
        GIVEN an authorised user with no roles
        WHEN the user tries to access any route
        THEN the user is redirected to the authenticator roles error page
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
        THEN the user is redirected to their dashboard
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
        assert b"lead-dashboard-stats" in response.data

    def test_authorised_assessor_redirected_to_dashboard(
        self, flask_test_client
    ):
        """
        GIVEN an authorised user
        WHEN the user tries to access the service "/" root
        THEN the user is redirected to their dashboard
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
        THEN the user is redirected to their dashboard
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

    @pytest.mark.parametrize(
        "claim,expect_scoring_available",
        [
            (test_commenter_claims, False),
            (test_assessor_claims, True),
            (test_lead_assessor_claims, True),
        ],
    )
    def test_different_user_levels_see_correct_sub_criteria_view(
        self, flask_test_client, claim, expect_scoring_available, mocker
    ):
        """
        GIVEN authorised users
        WHEN the user accesses the service sub_criteria root
        THEN the user sees the appropriate theme and navbar:
            - test commentor role can not see score in navbar
            - test assessor role can see score in navbar
            - test lead assessor role can see score in navbar
        Args:
            flask_test_client:

        Returns:

        """
        mocker.patch(
            "app.assess.models.ui.applicants_response.get_file_url",
            return_value="sample1.doc",
        )

        flask_test_client.set_cookie(
            "localhost",
            "fsd_user_token",
            create_valid_token(claim),
        )

        expected_theme_title = b"General information"
        response = flask_test_client.get(
            "assess/application_id/app_123/sub_criteria_id/"
            "1a2b3c4d?theme_id=general-information",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert expected_theme_title in response.data
        if expect_scoring_available:
            assert b"Score the subcriteria" in response.data
        else:
            assert b"Score the subcriteria" not in response.data

    @pytest.mark.parametrize(
        "claim,expect_all_comments_available",
        [
            (test_commenter_claims, False),
            (test_assessor_claims, True),
            (test_lead_assessor_claims, True),
        ],
    )
    def test_different_user_levels_see_correct_comments_on_sub_criteria_view(
        self, flask_test_client, claim, expect_all_comments_available, mocker
    ):
        """
        GIVEN authorised users
        WHEN the user accesses the service sub_criteria root
        THEN the user sees the appropriate comments based on role permissions:
            - test commenter can not see comment set by assessor
            - test commenter can not see comment set by lead assessor
            - test commenter can see comment set by commenter
            - test assessor can see all comments
            - test lead assessor can see all comments
        Args:
            flask_test_client:

        Returns:

        """
        mocker.patch(
            "app.assess.models.ui.applicants_response.get_file_url",
            return_value="sample1.doc",
        )

        flask_test_client.set_cookie(
            "localhost",
            "fsd_user_token",
            create_valid_token(claim),
        )

        expected_theme_title = b"General information"
        response = flask_test_client.get(
            "assess/application_id/app_123/sub_criteria_id/1a2b3c4d?"
            "theme_id=general-information",
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert expected_theme_title in response.data
        assert b"Thor" in response.data
        if expect_all_comments_available:
            assert b"Gommez Addams" in response.data
            assert b"Bruce Wayne" in response.data
        else:
            assert b"Gommez Addams" not in response.data
            assert b"Bruce Wayne" not in response.data
