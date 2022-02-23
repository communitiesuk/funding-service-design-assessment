from flask import abort
from flask import redirect
from flask import render_template
from flask.views import MethodView
from flask_wtf import FlaskForm
from wtforms import HiddenField
from wtforms import PasswordField
from wtforms import RadioField
from wtforms import StringField
from wtforms import TextAreaField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import URL
from app.assess.data import get_fund, get_application
from flask import url_for


class AssessQuestionView(MethodView):
    def __init__(self, *args, **kwargs):
        super(AssessQuestionView, self).__init__(*args, **kwargs)
        self.fund = None
        self.application = None
        self.current_question = None

    def set_fund(self, fund_id: str):
        self.fund = get_fund(fund_id)

    def set_application(self, fund_id: str, application_id: str):
        self.application = get_application(fund_id, application_id)

    def set_question(self, index: int):
        self.current_question = self.application.get_question(int(index))

    def set_field_attributes(self, form):
        for field in self.current_question.fields:
            d_field = getattr(form, field.name)
            for attr in [
                "label",
                "hint",
                "placeholder_text",
                "help_text",
                "field_type",
                "classes",
            ]:
                setattr(d_field, attr, getattr(field, attr))

            if hasattr(d_field, "choices"):
                choice_items = []
                if d_field.choices and len(d_field.choices) > 0:
                    choice_items = [
                        {"value": value, "text": text}
                        for value, text in d_field.choices
                    ]
                setattr(d_field, "choice_items", choice_items)

    def set_error_list(self, form):
        error_list = []
        for key, error in form.errors.items():
            error_list.append({"text": error[0], "href": "#" + key})
        setattr(form, "error_list", error_list)

    def form(self):
        class DynamicForm(FlaskForm):
            pass

        for f in self.current_question.fields:

            setattr(DynamicForm, f.name, self.get_field(f))

        d = DynamicForm()
        self.set_field_attributes(d)

        return d

    def get(self, fund_id: str, round_id: str, application_id: str, question_id: int):
        question_index = int(question_id)-1
        self.set_fund(fund_id)
        if not self.fund:
            abort(404)

        self.set_application(
            fund_id=fund_id,
            application_id=application_id)
        if not self.application:
            abort(404)

        if len(self.application.questions) <= question_index:
            return redirect(url_for("assess_bp.application",
                                    fund_id=fund_id,
                                    round_id=round_id,
                                    application_id=application_id))
        self.set_question(question_index)
        if not self.current_question:
            abort(404)

        return render_template(
            "question.html",
            fund=self.fund,
            round_id=round_id,
            application=self.application,
            question=self.current_question,
            question_id=int(question_id),
            final_question=len(self.application.questions) == question_index+1
        )

    def post(self, fund_id: str, round_id: str, application_id: str, question_id: int):
        question_index = int(question_id)-1
        self.set_fund(fund_id)
        if not self.fund:
            abort(404)

        self.set_application(
            fund_id=fund_id,
            application_id=application_id)
        if not self.application:
            abort(404)

        self.set_question(question_index)
        if not self.current_question:
            abort(404)

        form = self.form()

        print("This is the data : " + str(form.data))
        if form.validate_on_submit():
            print("Validated")
            return redirect(url_for(
                "application_question",
                fund_id=fund_id,
                round_id=round_id,
                application_id=application_id,
                question_id=question_id+1)
            )
        else:
            self.set_error_list(form)
            print("Invalid")

        return render_template(
            "question.html",
            form=form,
            fund=self.fund,
            round_id=round_id,
            application=self.application,
            question=self.current_question,
            question_id=int(question_id),
            final_question=len(self.application.questions) == question_index+1
        )

    def get_field(self, field):
        validators = []
        choices = []

        if field.field_type == "WebsiteField":
            validators.append(
                URL(
                    message=(
                        "Please enter a valid web address eg."
                        " https://www.yoursite.com"
                    )
                )
            )

        if field.field_type == "EmailAddressField":
            validators.append(
                Email(
                    message=(
                        "Please enter a valid email address eg."
                        " you@somedomain.com"
                    )
                )
            )

        if field.required:
            validators.append(DataRequired(field.required))

        if hasattr(field, "choices"):
            print(field.choices)
            for choice in field.choices:
                choices.append((choice["value"], choice["text"]))

        if field.field_type in [
            "text",
            "TextField",
            "EmailAddressField",
            "TelephoneNumberField",
            "WebsiteField",
        ]:
            f = StringField(field.label, validators=validators)
        elif field.field_type in ["YesNoField"]:
            f = RadioField(
                field.label,
                choices=(("yes", "Yes"), ("no", "No")),
                validators=validators,
            )
        elif field.field_type in ["RadiosField"]:
            f = RadioField(field.label, choices=choices, validators=validators)
        elif field.field_type in ["MultilineTextField"]:
            f = TextAreaField(field.label, validators=validators)
        elif field.field_type == "password":
            f = PasswordField(field.label)
        else:
            f = HiddenField(field.name)

        return f
