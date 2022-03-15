from app.assess.data import get_application
from app.assess.data import get_fund
from app.assess.data import get_round
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

    def set_round(self, fund_id: str, round_id: str):
        self.round = get_round(fund_id, round_id)

    def set_application(self, fund_id: str, application_id: str):
        self.application = get_application(fund_id, application_id)

    def set_question(self, index: int):
        self.current_question = self.application.get_question(int(index))

    def set_view(
        self,
        fund_id: str,
        round_id: str,
        application_id: str,
        question_id: int,
    ):
        question_index = int(question_id) - 1

        self.set_fund(fund_id)
        if not self.fund:
            abort(404)

        self.set_round(fund_id, round_id)
        if not self.round:
            abort(404)

        self.set_application(fund_id=fund_id, application_id=application_id)
        if not self.application:
            abort(404)

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
        fund_id: str,
        round_id: str,
        application_id: str,
        question_id: int,
    ):
        question_index = self.set_view(
            fund_id, round_id, application_id, question_id
        )

        if question_index is None:
            return redirect(
                url_for(
                    "assess_bp.application",
                    fund_id=fund_id,
                    round_id=round_id,
                    application_id=application_id,
                )
            )

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
        fund_id: str,
        round_id: str,
        application_id: str,
        question_id: int,
    ):
        question_index = self.set_view(
            fund_id, round_id, application_id, question_id
        )
        if question_index is None:
            return redirect(
                url_for(
                    "assess_bp.application",
                    fund_id=fund_id,
                    round_id=round_id,
                    application_id=application_id,
                )
            )

        return redirect(
            url_for(
                "application_question",
                fund_id=fund_id,
                round_id=round_id,
                application_id=application_id,
                question_id=question_index + 2,
            )
        )
