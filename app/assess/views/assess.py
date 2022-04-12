from app.assess.data import get_application
from app.assess.data import get_fund
from app.assess.data import get_round_with_applications
from flask import abort
from flask import redirect
from flask import render_template
from flask import url_for
from flask.views import MethodView


class AssessQuestionView(MethodView):
    def __init__(self, *args, **kwargs):
        super(AssessQuestionView, self).__init__(*args, **kwargs)
        self.fund = None
        self.round = None
        self.application = None
        self.current_question = None

    def set_fund(self, fund_id: str):
        self.fund = get_fund(fund_id)
        if not self.fund:
            abort(404)

    def set_round(self, round_id: str):
        self.round = get_round_with_applications(
            self.fund.identifier, round_id
        )
        if not self.round:
            abort(404)

    def set_application(self, application_id: str):
        self.application = get_application(application_id)
        if not self.application:
            abort(404)

        self.set_fund(self.application.fund_id)
        self.set_round(self.application.round_id)

    def set_question(self, index: int):
        self.current_question = self.application.get_question(int(index))

    def set_view(
        self,
        application_id: str,
        question_id: int,
    ):
        question_index = int(question_id) - 1

        self.set_application(application_id=application_id)

        if (
            question_index < 0
            or len(self.application.questions) <= question_index
        ):
            return None
        self.set_question(question_index)
        if not self.current_question:
            abort(404)
        return question_index

    def get(
        self,
        application_id: str,
        question_id: int,
    ):
        question_index = self.set_view(application_id, question_id)

        return render_template(
            "question.html",
            fund=self.fund,
            round=self.round,
            application=self.application,
            question=self.current_question,
            question_id=int(question_id),
            final_question=len(self.application.questions)
            == question_index + 1,
        )

    def post(
        self,
        application_id: str,
        question_id: int,
    ):
        question_index = self.set_view(application_id, question_id)

        return redirect(
            url_for(
                "application_question",
                application_id=application_id,
                question_id=question_index + 2,
            )
        )
