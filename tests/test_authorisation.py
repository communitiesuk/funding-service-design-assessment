import pytest
from bs4 import BeautifulSoup
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
        THEN the user is redirected to the "/" route
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
        THEN the user is redirected to the "/" route
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

    def test_any_unauthorised_visit_to_route_prompts_user_to_sign_in(
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
        assert b"Welcome to the assessment tool" in response.data
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

    @pytest.mark.mock_parameters(
        {
            "get_assessment_stats_path": (
                "app.assess.models.fund_summary.get_assessments_stats"
            ),
            "get_rounds_path": "app.assess.models.fund_summary.get_rounds",
            "fund_id": "test-fund",
            "round_id": "test-round",
        }
    )
    @pytest.mark.parametrize(
        "creds",
        [
            (test_commenter_claims),
            (test_assessor_claims),
            (test_lead_assessor_claims),
        ],
    )
    def test_authorised_roles_redirected_to_dashboard(
        self,
        flask_test_client,
        creds,
        templates_rendered,
        mock_get_funds,
        mock_get_rounds,
        mock_get_assessment_stats,
    ):
        """
        GIVEN an authorised user
        WHEN the user tries to access the service "/" route
        THEN the user is redirected to their dashboard
        Args:
            flask_test_client:

        Returns:

        """
        flask_test_client.set_cookie(
            "localhost",
            "fsd_user_token",
            create_valid_token(creds),
        )
        response = flask_test_client.get("/")
        assert response.status_code == 302
        assert response.location == Config.DASHBOARD_ROUTE

        response = flask_test_client.get("/", follow_redirects=True)
        assert 200 == response.status_code
        assert 1 == len(templates_rendered)
        rendered_template = templates_rendered[0]
        assert "assessor_tool_dashboard.html" == rendered_template[0].name

    @pytest.mark.parametrize(
        "claims,ability_to_score",
        [
            (test_commenter_claims, False),
            (test_assessor_claims, True),
            (test_lead_assessor_claims, True),
        ],
    )
    @pytest.mark.application_id("resolved_app")
    @pytest.mark.sub_criteria_id("test_sub_criteria_id")
    def test_scoring_permissions_for_users(
        self,
        flask_test_client,
        request,
        mock_get_sub_criteria,
        mock_get_fund,
        mock_get_latest_flag,
        mock_get_comments,
        mock_get_sub_criteria_theme,
        claims,
        ability_to_score,
    ):
        # Mocking fsd-user-token cookie
        token = create_valid_token(claims)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)

        # Send a request to the route you want to test
        application_id = request.node.get_closest_marker(
            "application_id"
        ).args[0]
        sub_criteria_id = request.node.get_closest_marker(
            "sub_criteria_id"
        ).args[0]

        response = flask_test_client.get(
            f"/assess/application_id/{application_id}/sub_criteria_id/{sub_criteria_id}"  # noqa
        )

        # Assert that the response has the expected status code
        assert 200 == response.status_code, "Wrong status code on response"

        soup = BeautifulSoup(response.data, "html.parser")
        assert (
            soup.title.string
            == "test_theme_name - test_sub_criteria - Project In prog and"
            " Res -"
            " Assessment Hub"
        )
        if ability_to_score:
            assert (
                b"score-subcriteria-link" in response.data
                and b"Score the subcriteria" in response.data
            ), (
                "Sidebar should contain score subcriteria link or link to"
                f" score subcriteria: {response.data}"
            )
        else:
            assert (
                b"score-subcriteria-link" not in response.data
                and b"Score the subcriteria" not in response.data
            ), (
                "Sidebar should not contain score subcriteria link or link to"
                f" score subcriteria: {response.data}"
            )

    @pytest.mark.parametrize(
        "claim,expect_all_comments_available",
        [
            (test_commenter_claims, False),
            (test_assessor_claims, True),
            (test_lead_assessor_claims, True),
        ],
    )
    @pytest.mark.application_id("resolved_app")
    @pytest.mark.sub_criteria_id("test_sub_criteria_id")
    def test_different_user_levels_see_correct_comments_on_sub_criteria_view(
        self,
        flask_test_client,
        request,
        claim,
        expect_all_comments_available,
        mock_get_sub_criteria,
        mock_get_fund,
        mock_get_latest_flag,
        mock_get_comments,
        mock_get_sub_criteria_theme,
    ):
        """
        GIVEN authorized users
        WHEN the user accesses the service sub_criteria route
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
        flask_test_client.set_cookie(
            "localhost",
            "fsd_user_token",
            create_valid_token(claim),
        )

        # Send a request to the route you want to test
        application_id = request.node.get_closest_marker(
            "application_id"
        ).args[0]
        sub_criteria_id = request.node.get_closest_marker(
            "sub_criteria_id"
        ).args[0]

        response = flask_test_client.get(
            f"/assess/application_id/{application_id}/sub_criteria_id/{sub_criteria_id}",  # noqa
            follow_redirects=True,
        )
        assert response.status_code == 200
        is_commenter_comment_visible = b"Im a commenter" in response.data
        is_assessor_comment_visible = b"Im an assessor" in response.data
        is_lead_assessor_comment_visible = (
            b"This is a comment" in response.data
        )

        if expect_all_comments_available:
            assert is_lead_assessor_comment_visible
            assert is_assessor_comment_visible
            assert is_commenter_comment_visible
        else:
            assert not is_lead_assessor_comment_visible
            assert not is_assessor_comment_visible
            assert is_commenter_comment_visible

    @pytest.mark.parametrize(
        "claim,expect_continue_available",
        [
            (test_commenter_claims, False),
            (test_assessor_claims, False),
            (test_lead_assessor_claims, True),
        ],
    )
    @pytest.mark.application_id("stopped_app")
    def test_user_levels_have_correct_permissions_to_restart_an_assessment(
        self,
        flask_test_client,
        request,
        claim,
        expect_continue_available,
        mock_get_latest_flag,
        mock_get_sub_criteria_banner_state,
        mock_get_fund,
    ):
        """
        GIVEN authorised users
        WHEN the user accesses the continue assessment route
        THEN the user sees the appropriate page:
            - commenter role cannot continue assessment
            - assessor role cannot continue assessment
            - lead assessor role can continue assessment
        """
        application_id = request.node.get_closest_marker(
            "application_id"
        ).args[0]
        flask_test_client.set_cookie(
            "localhost",
            "fsd_user_token",
            create_valid_token(claim),
        )

        if not expect_continue_available:
            with pytest.raises(RuntimeError) as exec_info:
                flask_test_client.get(
                    f"assess/continue_assessment/{application_id}",
                    follow_redirects=True,
                )
            # Tries to redirect to authenticator
            assert (
                str(exec_info.value)
                == "Following external redirects is not supported."
            )
        else:
            response = flask_test_client.get(
                f"assess/continue_assessment/{application_id}",
                follow_redirects=True,
            )
            assert response.status_code == 200
            assert b"Continue assessment" in response.data
            assert b"Reason for continuing assessment" in response.data

    @pytest.mark.parametrize(
        "claim,expect_flagging",
        [
            (test_commenter_claims, False),
            (test_assessor_claims, True),
            (test_lead_assessor_claims, True),
        ],
    )
    @pytest.mark.application_id("resolved_app")
    def test_different_user_levels_have_correct_flagging_permissions(
        self,
        request,
        flask_test_client,
        claim,
        expect_flagging,
        mock_get_latest_flag,
        mock_get_assessor_tasklist_state,
        mock_get_sub_criteria_banner_state,
        mock_get_fund,
    ):
        """
        GIVEN authorised users
        WHEN the user accesses the service flagging route
        THEN the user sees the appropriate page:
            - commenter role can not flag
            - assessor role can flag
            - lead assessor role can flag
        """

        application_id = request.node.get_closest_marker(
            "application_id"
        ).args[0]

        flask_test_client.set_cookie(
            "localhost",
            "fsd_user_token",
            create_valid_token(claim),
        )

        if not expect_flagging:
            with pytest.raises(RuntimeError) as exec_info:
                flask_test_client.get(
                    f"assess/flag/{application_id}",
                    follow_redirects=True,
                )
            # Tries to redirect to authenticator
            assert (
                str(exec_info.value)
                == "Following external redirects is not supported."
            )
        else:
            response = flask_test_client.get(
                f"assess/flag/{application_id}",
                follow_redirects=True,
            )
            assert response.status_code == 200
            assert b"Flag application" in response.data

    @pytest.mark.parametrize(
        "claim,expect_flagging",
        [
            (test_commenter_claims, False),
            (test_assessor_claims, False),
            (test_lead_assessor_claims, True),
        ],
    )
    @pytest.mark.application_id("resolved_app")
    @pytest.mark.flag_id("resolved_app")
    def test_different_user_levels_have_correct_permissions_to_resolve_flag(
        self,
        flask_test_client,
        request,
        claim,
        expect_flagging,
        mock_get_latest_flag,
        mock_get_assessor_tasklist_state,
        mock_get_flag,
        mock_get_sub_criteria_banner_state,
        mock_get_fund,
    ):
        """
        GIVEN authorised users
        WHEN the user accesses the resolve flag route
        THEN the user sees the appropriate page:
            - commentor role cannot resolve flag
            - assessor role cannot resolve flag
            - lead assessor role can resolve flag
        """
        application_id = request.node.get_closest_marker(
            "application_id"
        ).args[0]

        flag_id = request.node.get_closest_marker("flag_id").args[0]

        flask_test_client.set_cookie(
            "localhost",
            "fsd_user_token",
            create_valid_token(claim),
        )
        if not expect_flagging:
            with pytest.raises(RuntimeError) as exec_info:
                flask_test_client.get(
                    f"assess/resolve_flag/{application_id}",
                    follow_redirects=True,
                )
            # Tries to redirect to authenticator
            assert (
                str(exec_info.value)
                == "Following external redirects is not supported."
            )
        else:
            response = flask_test_client.get(
                f"assess/resolve_flag/{application_id}?flag_id={flag_id}",
                follow_redirects=True,
            )
            assert response.status_code == 200
            assert b"Resolve flag" in response.data
            assert b"Query resolved" in response.data
            assert b"Stop assessment" in response.data

    @pytest.mark.parametrize(
        "user_account, expect_flagging",
        [
            (test_commenter_claims, False),
            (test_assessor_claims, False),
            (test_lead_assessor_claims, True),
        ],
    )
    @pytest.mark.application_id("flagged_qa_completed_app")
    def test_resolve_flag_option_shows_for_correct_permissions(
        self,
        flask_test_client,
        request,
        user_account,
        expect_flagging,
        mock_get_assessor_tasklist_state,
        mock_get_fund,
        mock_get_round,
        mock_get_latest_flag,
        mock_get_bulk_accounts,
    ):
        token = create_valid_token(user_account)
        flask_test_client.set_cookie("localhost", "fsd_user_token", token)
        application_id = request.node.get_closest_marker(
            "application_id"
        ).args[0]

        response = flask_test_client.get(
            f"assess/application/{application_id}"
        )
        assert response.status_code == 200
        if expect_flagging:
            assert b"Resolve flag" in response.data
        else:
            assert b"Resolve flag" not in response.data
