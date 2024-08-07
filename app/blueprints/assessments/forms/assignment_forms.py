from flask import request
from flask_wtf import FlaskForm


class AssessmentAssignmentForm(FlaskForm):
    def validate(self, extra_validators=None):
        if super().validate(extra_validators):
            if request.referrer != request.url:
                # From a redirect, not a form post
                return False

            if not request.form.getlist("selected_assessments"):
                self.form_errors.append("At least one assessment should be selected")
                return False
            else:
                return True

        return False


class AssessorTypeForm(FlaskForm):
    def validate(self, extra_validators=None):
        if super().validate(extra_validators):
            if request.referrer != request.url:
                # From a redirect, not a form post
                return False

            if not request.form.getlist("assessor_role"):
                self.form_errors.append("An assessor type should be selected")
                return False
            else:
                return True

        return False


class AssessorChoiceForm(FlaskForm):
    def validate(self, extra_validators=None):
        if super().validate(extra_validators):
            if request.referrer != request.url:
                # From a redirect, not a form post
                return False

            if not request.form.getlist("selected_users"):
                self.form_errors.append("At least one assessor should be selected")
                return False
            else:
                return True

        return False


class AssignmentOverviewForm(FlaskForm):
    def validate(self, extra_validators=None):
        if super().validate(extra_validators):
            if request.referrer != request.url:
                # From a redirect, not a form post
                return False

            passed_validation = True
            if not request.form.getlist("selected_users"):
                self.form_errors.append("At least one assessor should be selected")
                passed_validation = False

            if not request.form.getlist("assessor_role"):
                self.form_errors.append("An assessor type should be selected")
                passed_validation = False

            if not request.form.getlist("selected_assessments"):
                self.form_errors.append("At least one assessment should be selected")
                passed_validation = False

            return passed_validation

        return False
