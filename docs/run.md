# Run Service

Run:

    flask run

A local dev server will be created on (PORT specified in FLASK_RUN_PORT environment variable)

    http://localhost:{{PORT}}

Flask environment variables are configurable in `.flaskenv`

## Local Authentication
The assessment app protects different parts of functionality by interrogating the roles of the logged in user. In order to test this locally where we don't have SSO available, a debug user is available. This bypassess login and puts the required information in the session to allow you to appear logged in when running locally. To enable this:
* You must be running with `FLASK_ENV=development` (the default for `flask run` or the docker runner)
* Update [DevelopmentConfig](../config/envs/development.py) so that `DEBUG_USER_ON=True`
* Supply the desired role for the debug user using environment variable `DEBUG_USER_ROLE`. eg. `DEBUG_USER_ROLE=ASSESSOR`
* Run the app and navigate to /assess/assessor_dashboard/, you will see the logged in view and be able to comment, score, flag etc.
* When running locally with the debug user enabled, you will also see a yellow box in the top right hand corner of all pages to state which user you are using and their role.

### Run with Gunicorn

In deployed environments the service is run with gunicorn. You can run the service locally with gunicorn to test

First set the FLASK_ENV environment you wish to test eg:

    export FLASK_ENV=dev

Then run gunicorn using the following command:

    gunicorn wsgi:app -c run/gunicorn/local.py

## Pipelines

These are the current pipelines running on the repo:

* Deploy to Gov PaaS - This is a simple pipeline to demonstrate capabilities.  Builds, tests and deploys a simple python application to the PaaS for evaluation in Dev and Test environments only.
* s3-zip - Tags every commit to main for release
