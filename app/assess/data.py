import json
import os
from typing import List
from app.config import FUND_STORE_API_ROOT
from app.config import APPLICATION_STORE_API_ROOT
from app.config import APPLICATION_ROOT
from datetime import datetime
import requests
from slugify import slugify


# Fund Store Endpoints
FUNDS_ENDPOINT = "funds"
FUND_ENDPOINT = "funds/{fund_id}"
ROUND_ENDPOINT = "funds/{fund_id}/round/{round_id}"

# Application Store Endpoints
APPLICATIONS_ENDPOINT = "fund/{fund_id}"
APPLICATION_ENDPOINT = "fund/{fund_id}/application/{application_id}"


class QuestionField(object):

    def __init__(
            self,
            key: str,
            title: str,
            field_type: str,
            answer: str,
    ):
        self.key = key
        self.title = title
        self.field_type = field_type
        self.answer = answer

    @staticmethod
    def from_json(data: dict):
        return QuestionField(
            key=data.get("key"),
            title=data.get("title"),
            field_type=data.get("field_type"),
            answer=data.get("answer")
        )


class Question(object):

    def __init__(
            self,
            title: str,
            fields: List[QuestionField] = None
    ):
        self.title = title
        self.fields = fields

    @staticmethod
    def from_json(data: dict):
        question = Question(
            title=data.get("question")
        )
        if "fields" in data:
            for field_data in data["fields"]:
                field = QuestionField.from_json(field_data)
                question.add_field(field)
        return question

    def add_field(self, field: QuestionField):
        if not self.fields:
            self.fields = []
        self.fields.append(field)


class Application(object):

    def __init__(
            self,
            identifier: str,
            submitted: datetime,
            fund_name: str,
            submission: dict,
            questions: List[Question] = None,
    ):
        self.identifier = identifier
        self.submitted = submitted
        self.fund_name = fund_name
        self.submission = submission
        self.questions = questions

    @staticmethod
    def from_json(data: dict):
        application = Application(
            identifier=data.get("identifier"),
            submitted=data.get("submitted"),
            fund_name=data.get("fund_name"),
            submission=data.get("submission")
        )
        if application.submission and "questions" in application.submission:
            for question_data in application.submission["questions"]:
                question = Question.from_json(question_data)
                application.add_question(question)

        return application

    def add_question(self, question: Question):
        if not self.questions:
            self.questions = []
        self.questions.append(question)

    def get_question(self, index: int):
        if self.questions:
            return self.questions[index]
        return None


class Round(object):

    def __init__(
            self,
            fund_name: str,
            opens: datetime,
            deadline: datetime,
            identifier: str = None,
            fund_identifier: str = None,
            applications: List[Application] = None
    ):
        self.fund_name = fund_name
        self._identifier = identifier
        self._fund_identifier = fund_identifier
        self.opens = opens
        self.deadline = deadline
        self.applications = applications

    @property
    def identifier(self):
        if self._identifier:
            return self._identifier
        return slugify(self.deadline)

    @identifier.setter
    def identifier(self, value):
        self._identifier = value

    @identifier.deleter
    def identifier(self):
        del self._identifier

    @property
    def fund_identifier(self):
        if self._fund_identifier:
            return self._fund_identifier
        return slugify(self.fund_name)

    @fund_identifier.setter
    def fund_identifier(self, value):
        self._fund_identifier = value

    @fund_identifier.deleter
    def fund_identifier(self):
        del self._fund_identifier

    @staticmethod
    def from_json(data: dict):
        return Round(
            fund_name=data.get("fund_name"),
            opens=data.get("opens"),
            deadline=data.get("deadline"),
            identifier=data.get("identifier"),
            fund_identifier=data.get("fund_identifier")
        )

    def add_application(self, application: Application):
        if not self.applications:
            self.applications = []
        self.applications.append(application)


class Fund(object):

    def __init__(
        self,
        name: str,
        identifier: str = None,
        rounds: List[Round] = None,
    ):
        self.name = name
        self.rounds = rounds
        self._identifier = identifier

    @property
    def identifier(self):
        if self._identifier:
            return self._identifier
        return slugify(self.name)

    @identifier.setter
    def identifier(self, value):
        self._identifier = value

    @identifier.deleter
    def identifier(self):
        del self._identifier

    @staticmethod
    def from_json(data: dict):
        return Fund(
            name=data.get("name"),
            identifier=data.get("identifier")
        )

    def add_round(self, fund_round: Round):
        if not self.rounds:
            self.rounds = []
        self.rounds.append(fund_round)


def get_data(endpoint: str):
    if endpoint[:4] == "http":
        data = requests.get(endpoint)
    else:
        data = get_local_data(endpoint)
    return data


def get_local_data(path: str):
    data_path = os.path.join(APPLICATION_ROOT, path, "data.json")
    fp = open(data_path)
    data = json.load(fp)
    return data


def get_funds() -> List[Fund] | None:
    endpoint = FUND_STORE_API_ROOT + FUNDS_ENDPOINT
    response = get_data(endpoint)
    if len(response) > 0:
        funds = []
        for fund in response:
            funds.append(Fund.from_json(fund))
        return funds
    return None


def get_fund(fund_id: str) -> Fund | None:
    endpoint = FUND_STORE_API_ROOT + FUND_ENDPOINT.format(
        fund_id=fund_id
    )
    response = get_data(endpoint)
    if "name" in response:
        fund = Fund.from_json(response)
        if "rounds" in response and len(response["rounds"]) > 0:
            for fund_round in response["rounds"]:
                new_round = Round.from_json(fund_round)
                fund.add_round(new_round)
        return fund
    return None


def get_round(fund_id: str, identifier: str) -> Round | None:
    round_endpoint = FUND_STORE_API_ROOT + ROUND_ENDPOINT.format(
        fund_id=fund_id, round_id=identifier
    )
    round_response = get_data(round_endpoint)
    applications_endpoint = APPLICATION_STORE_API_ROOT + APPLICATIONS_ENDPOINT.format(
        fund_id=fund_id
    )
    applications_response = get_data(applications_endpoint)
    if "fund_name" in round_response:
        fund_round = Round.from_json(round_response)
        if "applications" in applications_response \
                and len(applications_response["applications"]) > 0:
            for application in applications_response["applications"]:
                fund_round.add_application(
                    Application.from_json(application)
                )

        return fund_round
    return None


def get_application(fund_id: str, identifier: str) -> Application | None:
    application_endpoint = APPLICATION_STORE_API_ROOT + APPLICATION_ENDPOINT.format(
        fund_id=fund_id,
        application_id=identifier
    )
    application_response = get_data(application_endpoint)
    if "submitted" in application_response and application_response["submitted"]:
        application = Application.from_json(application_response)

        return application
    return None


