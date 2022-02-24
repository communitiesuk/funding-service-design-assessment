import json
import os
from typing import List
from app.config import FUND_STORE_API_HOST
from app.config import APPLICATION_STORE_API_HOST
from app.config import FLASK_ROOT
from datetime import datetime
import requests
from slugify import slugify


# Fund Store Endpoints
FUNDS_ENDPOINT = "/funds/"
FUND_ENDPOINT = "/funds/{fund_id}"
ROUND_ENDPOINT = "/funds/{fund_id}/round/{round_number}"

# Application Store Endpoints
APPLICATIONS_ENDPOINT = "/fund/{fund_id}?datetime_start={datetime_start}&datetime_end={datetime_end}"
APPLICATION_ENDPOINT = "/fund/{fund_id}?application_id={application_id}"


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
            questions: List[Question] = None,
    ):
        self.identifier = identifier
        self.submitted = submitted
        self.fund_name = fund_name
        self.questions = questions

    @staticmethod
    def from_json(data: dict):
        application = Application(
            identifier=data.get("id"),
            submitted=datetime.fromisoformat(data.get("date_submitted")),
            fund_name=data.get("fund_name")
        )
        if "questions" in data:
            for question_data in data["questions"]:
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
            opens: datetime,
            deadline: datetime,
            identifier: str = None,
            applications: List[Application] = None
    ):
        self._identifier = identifier
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


    @staticmethod
    def from_json(data: dict):
        return Round(
            opens=data.get("opens"),
            deadline=data.get("deadline"),
            identifier=str(data.get("round_identifer"))  # This is a temporary typo
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
        response = requests.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            print(data)
        else:
            return None
            # raise Exception("API request for "+endpoint+" returned "+str(response.status_code))

    else:
        data = get_local_data(endpoint)
    return data


def get_local_data(path: str):
    data_path = os.path.join(FLASK_ROOT, path, "data.json")
    fp = open(data_path)
    data = json.load(fp)
    fp.close()
    return data


def get_funds() -> List[Fund] | None:
    endpoint = FUND_STORE_API_HOST + FUNDS_ENDPOINT
    response = get_data(endpoint)
    if response and len(response) > 0:
        funds = []
        for fund in response:
            funds.append(Fund.from_json(fund))
        return funds
    return None


def get_fund(fund_id: str) -> Fund | None:
    endpoint = FUND_STORE_API_HOST + FUND_ENDPOINT.format(
        fund_id=fund_id
    )
    response = get_data(endpoint)
    if response and "name" in response:
        fund = Fund.from_json(response)
        if "rounds" in response and len(response["rounds"]) > 0:
            for fund_round in response["rounds"]:
                new_round = Round.from_json(fund_round)
                fund.add_round(new_round)
        return fund
    return None


def get_round(fund_id: str, identifier: str) -> Round | None:
    round_endpoint = FUND_STORE_API_HOST + ROUND_ENDPOINT.format(
        fund_id=fund_id, round_number=identifier
    )
    round_response = get_data(round_endpoint)
    if round_response and "round_identifer" in round_response:  #This is a temporary typo
        fund_round = Round.from_json(round_response)
        applications_endpoint = APPLICATION_STORE_API_HOST + APPLICATIONS_ENDPOINT.format(
            fund_id=fund_id,
            datetime_start=fund_round.opens,
            datetime_end=fund_round.deadline
        )
        applications_response = get_data(applications_endpoint)
        if applications_response and len(applications_response.items()) > 0:
            for _, application in applications_response.items():
                fund_round.add_application(
                    Application.from_json(application)
                )

        return fund_round
    return None


def get_application(fund_id: str, identifier: str) -> Application | None:
    application_endpoint = APPLICATION_STORE_API_HOST + APPLICATION_ENDPOINT.format(
        fund_id=fund_id,
        application_id=identifier
    )
    application_response = get_data(application_endpoint)
    if application_response and "id" in application_response:
        application = Application.from_json(application_response)

        return application
    return None


