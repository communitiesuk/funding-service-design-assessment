from config import Config
from flask import g
from flask import redirect
from flask import request
from fsd_utils.authentication.models import User


def auth_protect(minimum_roles_required, unprotected_routes):
    """
    Checks the authentication and authorisation attributes of the
    user accessing the service and allows them to access the requested
    resource if authorised, or redirect them to login (or a permissions
    error message) if not authenticated/authorised.

    The function also incorporates support for bypassing authorisation
    via setting of a DEBUG_USER_ROLE env var which will mimic the effect
    of a user with that role (only used when FLASK_ENV is "development").

    Args:
        minimum_roles_required: List[str]
            - a list of minimum roles a user must have to access the service
        unprotected_routes: List[str]
            - a list of routes e.g. ["/"]
                that can be accessed without authentication

    Returns:
        redirect (302) or None if authorised

    """

    if (
        Config.FLASK_ENV == "development"
        and Config.DEBUG_USER_ROLE
        and not g.is_authenticated
    ):
        g.is_authenticated = True
        g.account_id = "dev-account-id"
        g.user = User(**Config.DEBUG_USER)
        if request.path in ["", "/"]:
            return redirect(Config.DASHBOARD_ROUTE)

    elif g.is_authenticated:
        # Ensure that authenticated users have
        # all minimum required roles
        if not g.user.roles or not all(
            role_required in g.user.roles
            for role_required in minimum_roles_required
        ):
            return redirect(
                Config.AUTHENTICATOR_HOST
                + "/service/user"
                + "?roles_required="
                + "|".join(minimum_roles_required)
            )
        elif request.path in ["", "/"]:
            return redirect(Config.DASHBOARD_ROUTE)
    elif (
        request.path not in unprotected_routes
        and not request.path.startswith("/static/")
    ):  # noqa
        # Redirect unauthenticated users to
        # login on the home page
        return redirect("/")
