# Funding Service Design - Assessment Hub

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
![Funding Service Design Frontend Deploy](https://github.com/communitiesuk/funding-service-design-assessment/actions/workflows/govcloud.yml/badge.svg)
[![CodeQL](https://github.com/communitiesuk/funding-service-design-assessment/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/communitiesuk/funding-service-design-assessment/actions/workflows/codeql-analysis.yml)

Repo for the DLUCH Funding Service Design Assessment Hub.

Built with Flask.

## Prerequisites
- python ^= 3.10

# Getting started

## Installation

Clone the repository

### Create a Virtual environment

    python3 -m venv .venv

### Enter the virtual environment

...either macOS using bash:

    source .venv/bin/activate

...or if on Windows using Command Prompt:

    .venv\Scripts\activate.bat

### Install dependencies

requirements-dev.txt and requirements.txt are updated using [pip-tools pip-compile](https://github.com/jazzband/pip-tools)
To update requirements please manually add the dependencies in the .in files (not the requirements.txt files)
Then run (in the following order):

    pip-compile requirements.in

    pip-compile requirements-dev.in

From the top-level directory enter the command to install pip and the dependencies of the project

    python3 -m pip install --upgrade pip && pip install -r requirements-dev.txt

## How to use
Enter the virtual environment as described above, then:

### Create static files

If you would like to manually download the static files and extract them then run

    python3 build.py

Developer note: If you receive a certification error when running the above command on macOS,
consider if you need to run the Python
'Install Certificates.command' which is a file located in your globally installed Python directory. For more info see [StackOverflow](https://stackoverflow.com/questions/52805115/certificate-verify-failed-unable-to-get-local-issuer-certificate)

Then run:

    flask run

A local dev server will be created on

    http://127.0.0.1:5000/

Flask environment variables are configurable in .flaskenv

You should see the following:
![Preview of the end result](https://user-images.githubusercontent.com/56394038/155768587-907ea46a-ade5-475a-a901-acfde6160f66.png)

# Configuration

This service is designed to be an interface to three primary data stores: The *Fund Store* which holds data about different funds, the *Round Store* which holds information about the rounds for each fund, and the *Application Store* which holds individual applications/submissions for each fund.

The locations of the APIs for these three stores can be set using the FUND_STORE_API_HOST,  ROUND_STORE_API_HOST and APPLICATION_STORE_API_HOST environment variables. Set these to the respective locations for each API host you want to use eg.:

    export FUND_STORE_API_HOST="https://dluhc-fsd-fund-store-api.gov.uk"
    export ROUND_STORE_API_HOST="https://dluhc-fsd-round-store-api.gov.uk"
    export APPLICATION_STORE_API_HOST="https://dluhc-fsd-application-store-api.gov.uk"

# Pipelines

These are the current pipelines running on the repo:

* Deploy to Gov PaaS - This is a simple pipeline to demonstrate capabilities.  Builds, tests and deploys a simple python application to the PaaS for evaluation in Dev and Test Only.
* NOTE: THIS IS A CUSTOM DEPLOY WORKFLOW AND DOES NOT YET USE THE WORKFLOW TEMPLATE FOR FUNDING SERVICE DESIGN PENDING UPDATE

# Testing

## Unit & Accessibility Testing

To run all tests including aXe accessibility tests (using Chrome driver for Selenium) in a development environment run:

    pytest

The aXe reports are printed at /axe_reports


## Performance Testing

Performance tests are stored in a separate repository which is then run in the pipeline. If you want to run the performance tests yourself follow the steps in the README for the performance test repo located [here](https://github.com/communitiesuk/funding-service-design-performance-tests/blob/main/README.md)


# Extras

This repo comes with a .pre-commit-config.yaml, if you wish to use this do
the following while in your virtual enviroment:

    pip install pre-commit black

    pre-commit install

Once the above is done you will have autoformatting and pep8 compliance built
into your workflow. You will be notified of any pep8 errors during commits.
