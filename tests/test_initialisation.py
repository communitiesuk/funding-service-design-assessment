"""
Some very basic tests. Tests if the flask client spins
up and serves the index. This is a selected subset
of the test_routes.py test. These tests are marked
"init" so that github actions can run them before
the other tests. This saves time.
This is the most basic set of tests.
"""


def test_flask_initiates(flask_test_client):
    """
    GIVEN Our Flask Application
    WHEN the '/' page (index) is requested (GET)
    THEN check that the get response is successful.
    If this test succeeds then our flask application
    is AT LEAST up and running without errors.
    """
    response = flask_test_client.get("/", follow_redirects=True)
    assert response.status_code == 200
