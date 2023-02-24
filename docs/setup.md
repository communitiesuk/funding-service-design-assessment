# Set-up Service

## **Prerequisites**

### Python and Flask version
See requirements.in file

## **Clone the repository**

### Create a Virtual environment

    python3 -m venv .venv

### Enter the virtual environment

...either macOS using bash:

    source .venv/bin/activate

...or if on Windows using Command Prompt:

    .venv\Scripts\activate.bat

## **Dependencies**

### Install dependencies

From the top-level directory enter the following command to install pip and the dependencies of the project, including local development dependencies:

    python3 -m pip install --upgrade pip && pip install -r requirements-dev.txt

### Add dependencies

requirements-dev.txt and requirements.txt are updated using [pip-tools pip-compile](https://github.com/jazzband/pip-tools).

To update project requirements add the dependencies into the .in files (not the .txt files) and run (in the following order):

    pip-compile requirements.in

    pip-compile requirements-dev.in

If the packages listed in the .txt files do not meet those specified in the .in files (including version restrictions), the previous commands will update the .txt files accordingly.

Then to install the upgraded dependencies:

    pip install -r requirements-dev.txt

### Upgrade existing dependencies

This repository uses GitHub's [Dependabot](https://github.com/dependabot) to keep the repository requirements up to date. The following Dependabot tools are active:

- Dependabot alerts
Alerts for vulnerabilities that affect dependencies and generates Dependabot pull requests to resolve these vulnerabilities.

- Dependabot security updates
Dependabot opens pull requests automatically to resolve Dependabot alerts.

- Dependabot version updates
Dependabot opens pull requests automatically to keep dependencies up-to-date when new versions are available. This can be configured in the **dependabot.yml** file within the repositories '.github' folder.

**Manually upgrade dependencies**

To ensure that dependencies are using the most recent compatible versions available we can run a pip-tools upgrade. To upgrade dependency versions in the existing .txt files, run (in the following order):

    pip-compile requirements.in --upgrade

    pip-compile requirements-dev.in --upgrade

This will upgrade the versions in the .txt files, whilst maintaining the version restrictions specified in the .in files.

Then to install the upgraded dependencies locally:

    pip install -r requirements-dev.txt

## Assets

### Build Static Assets

This build step imports assets required for the GovUK template and styling components.
It also builds customised swagger files which slightly clean the layout provided by the vanilla SwaggerUI 3.52.0 (which is included in dependency swagger-ui-bundle==0.0.9) are located at /swagger/custom/3_52_0.

Before first usage, the vanilla bundle needs to be imported and overwritten with the modified files. To do this run:

    python3 build.py

Developer note: If you receive a certification error when running the above command on macOS,
consider if you need to run the Python
'Install Certificates.command' which is a file located in your globally installed Python directory. For more info see [StackOverflow](https://stackoverflow.com/questions/52805115/certificate-verify-failed-unable-to-get-local-issuer-certificate)

### Copying Styles
During development if you need to copy styles from `app/static/src/styles` to the `dist` dir, you can do this by running

    invoke copy-styles

This uses `invoke` and the tasks defined in `tasks.py` to just copy the contents of the source styles directory to dist, saving the time to reinstall the whole govuk bundle by running the full build as above.

## Configuration

This service is designed to be an interface to multiple other services: The *Fund Store* which holds data about different funds and their rounds, and the *Application Store* which holds individual applications/submissions for each fund.

The locations of the APIs for these services can be set using the following environment variables.

- ASSESSMENT_STORE_API_HOST ([Go to repo](https://github.com/communitiesuk/funding-service-design-assessment-store))
- ACCOUNT_STORE_API_HOST ([Go to repo](https://github.com/communitiesuk/funding-service-design-account-store))
- AUTHENTICATOR_HOST ([Go to repo](https://github.com/communitiesuk/funding-service-design-authenticator))
- FUND_STORE_API_HOST ([Go to repo](https://github.com/communitiesuk/funding-service-design-fund-store))
- APPLICATION_STORE_API_HOST ([Go to repo](https://github.com/communitiesuk/funding-service-design-application-store))

## Extras

This repo comes with a .pre-commit-config.yaml, if you wish to use this do
the following while in your virtual enviroment:

    pre-commit install

Once the above is done you will have autoformatting and pep8 compliance built
into your workflow. You will be notified of any pep8 errors during commits.
