import datetime
from dataclasses import dataclass

import pytz
from app.blueprints.authentication.validation import AssessmentAccessController
from app.blueprints.authentication.validation import get_countries_from_roles
from app.blueprints.authentication.validation import (
    has_devolved_authority_validation,
)
from app.blueprints.services.data_services import get_assessments_stats
from app.blueprints.services.data_services import get_rounds
from app.blueprints.services.models.fund import Fund
from config import Config
from flask import url_for


@dataclass
class Stats:
    date: str
    total_received: int
    completed: int
    started: int
    qa_complete: int
    stopped: int


@dataclass
class FundSummary:
    is_active_status: bool
    fund_id: str
    round_id: str
    fund_name: str
    round_name: str
    application_stats: Stats
    assessments_href: str
    access_controller: AssessmentAccessController
    export_href: str
    assessment_tracker_href: str
    round_application_fields_download_available: bool


def create_fund_summaries(fund: Fund) -> list[FundSummary]:
    """Get all the round stats in a fund."""
    summaries = []
    for round in get_rounds(fund.id):
        # only show closed rounds in assessment unless `SHOW_ALL_ROUNDS`==True
        if Config.SHOW_ALL_ROUNDS or (not is_after_today(round.deadline)):
            # check for devolved_authority_validation
            if has_devolved_authority_validation(fund_id=fund.id):
                countries = get_countries_from_roles(fund.short_name)
                search_params = {"countries": ",".join(countries)}
                round_stats = get_assessments_stats(
                    fund.id, round.id, search_params
                )
            else:
                round_stats = get_assessments_stats(fund.id, round.id)
            summary = FundSummary(
                is_active_status=is_after_today(round.assessment_deadline),
                fund_id=fund.id,
                round_id=round.id,
                fund_name=fund.name,
                round_name=round.title,
                application_stats=Stats(
                    date=round.assessment_deadline,
                    total_received=round_stats["total"],
                    completed=round_stats["completed"],
                    started=round_stats["assessing"],
                    qa_complete=round_stats["qa_completed"],
                    stopped=round_stats["stopped"],
                ),
                assessments_href=url_for(
                    "assessment_bp.fund_dashboard",
                    fund_short_name=fund.short_name,
                    round_short_name=round.short_name.lower(),
                ),
                access_controller=AssessmentAccessController(fund.short_name),
                export_href=url_for(
                    "assessment_bp.assessor_export",
                    fund_short_name=fund.short_name,
                    round_short_name=round.short_name.lower(),
                    report_type="ASSESSOR_EXPORT",
                ),
                assessment_tracker_href=url_for(
                    "assessment_bp.assessor_export",
                    fund_short_name=fund.short_name,
                    round_short_name=round.short_name.lower(),
                    report_type="OUTPUT_TRACKER",
                ),
                round_application_fields_download_available=round.application_fields_download_available,
            )
            summaries.append(summary)
    return sorted(
        summaries, key=lambda s: s.application_stats.date, reverse=True
    )


def is_after_today(date_str: str):
    """Check if the provided datetime string has passed the current datetime"""
    uk_tz = pytz.timezone("Europe/London")
    date_format = "%Y-%m-%dT%H:%M:%S"
    dt = datetime.datetime.strptime(date_str, date_format)
    dt_uk = uk_tz.localize(dt)
    now_uk = datetime.datetime.now(tz=uk_tz)
    return dt_uk > now_uk
