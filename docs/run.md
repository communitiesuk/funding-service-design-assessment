# Run Service

Run:

    flask run

A local dev server will be created on (PORT specified in FLASK_RUN_PORT environment variable)

    http://localhost:{{PORT}}

Flask environment variables are configurable in `.flaskenv`

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
