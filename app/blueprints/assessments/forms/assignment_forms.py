from flask import request
from flask_wtf import FlaskForm


class AssessmentAssignmentForm(FlaskForm):
    def validate(self, extra_validators=None):
        if super().validate(extra_validators):
            if request.referrer != request.url:
                # From a redirect, not a form post
                return False

            if not (
                selected_assessments := request.form.getlist("selected_assessments")
            ):
                self.form_errors.append("At least one assessment should be selected")
                return False

            if len(selected_assessments) > 1:
                self.form_errors.append("At most one assessment should be selected")
                return False

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

            return True

        return False


class AssessorChoiceForm(FlaskForm):
    def validate(self, extra_validators=None):
        if super().validate(extra_validators):
            if request.referrer != request.url:
                # From a redirect, not a form post
                return False

            if set(request.form.getlist("assigned_users")) == set(
                request.form.getlist("selected_users")
            ):
                self.form_errors.append(
                    "No changes have been made to the current assignments for this application"
                )
                return False

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
