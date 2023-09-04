import datetime
from dataclasses import dataclass

import pytz
from app.blueprints.authentication.validation import AssessmentAccessController
from app.blueprints.authentication.validation import get_countries_from_roles
from app.blueprints.authentication.validation import (
    has_devolved_authority_validation,
)
from app.blueprints.services.data_services import get_application_stats
from app.blueprints.services.data_services import get_assessments_stats
from app.blueprints.services.data_services import get_rounds
from app.blueprints.services.models.fund import Fund
from config import Config
from config.display_value_mappings import ALL_VALUE
from config.display_value_mappings import LandingFilters
from flask import current_app
from flask import url_for
from fsd_utils.simple_utils.date_utils import (
    current_datetime_after_given_iso_string,
)
from fsd_utils.simple_utils.date_utils import (
    current_datetime_before_given_iso_string,
)


@dataclass
class Stats:
    date: str
    total_received: int
    completed: int
    started: int
    qa_complete: int
    stopped: int


@dataclass
class LiveRoundStats:
    closing_date: str
    not_started: int
    in_progress: int
    completed: int
    submitted: int


@dataclass
class RoundSummary:
    is_assessment_active_status: bool
    is_round_open_status: bool
    is_not_yet_open_status: bool
    fund_id: str
    round_id: str
    fund_name: str
    round_name: str
    assessments_href: str
    access_controller: AssessmentAccessController
    export_href: str
    assessment_tracker_href: str
    round_application_fields_download_available: bool
    sorting_date: str
    assessment_stats: Stats = None
    live_round_stats: LiveRoundStats = None


def create_round_summaries(
    fund: Fund, filters: LandingFilters
) -> list[RoundSummary]:
    """Get all the round stats in a fund."""
    access_controller = AssessmentAccessController(fund.short_name)

    summaries = []
    live_rounds = []
    round_id_to_summary_map = {}
    for round in get_rounds(fund.id):
        if _round_not_yet_open := current_datetime_before_given_iso_string(  # noqa
            round.opens
        ):
            if filters.filter_status not in (ALL_VALUE, "closed"):
                continue

            current_app.logger.info(
                f"Round {fund.short_name} - {round.short_name} is not yet open"
                f" (opens: {round.opens})"
            )
            application_stats = None
            sorting_date = round.assessment_deadline
            assessment_active = False
            round_open = False
            not_yet_open = True

        elif _round_currently_open := all(  # noqa
            [
                current_datetime_after_given_iso_string(round.opens),
                current_datetime_before_given_iso_string(round.deadline),
            ]
        ):
            if filters.filter_status not in (ALL_VALUE, "live"):
                continue

            if not access_controller.has_any_assessor_role:
                continue

            current_app.logger.info(
                f"Round {fund.short_name} - {round.short_name} is currently"
                f" open (opens: {round.opens}, closes: {round.deadline})"
            )
            live_rounds.append(round)
            application_stats = None
            sorting_date = round.deadline
            assessment_active = False
            round_open = True
            not_yet_open = False

        elif _round_assessment_active := any(  # noqa
            [
                current_datetime_before_given_iso_string(
                    round.assessment_deadline
                ),
                Config.SHOW_ALL_ROUNDS,  # For development or testing purposes
            ]
        ):
            if filters.filter_status not in (ALL_VALUE, "active"):
                continue

            current_app.logger.info(
                f"Round {fund.short_name} - {round.short_name} is active in"
                f" assessment (opens: {round.opens}, closes: {round.deadline},"
                f" asesssment deadline: {round.assessment_deadline})"
            )

            search_params = {}
            if has_devolved_authority_validation(fund_id=fund.id):
                countries = get_countries_from_roles(fund.short_name)
                search_params = {"countries": ",".join(countries)}

            round_stats = get_assessments_stats(
                fund.id, round.id, search_params
            )
            application_stats = Stats(
                date=round.assessment_deadline,
                total_received=round_stats["total"],
                completed=round_stats["completed"],
                started=round_stats["assessing"],
                qa_complete=round_stats["qa_completed"],
                stopped=round_stats["stopped"],
            )
            sorting_date = round.assessment_deadline
            assessment_active = True
            round_open = False
            not_yet_open = False

        else:  # Assessment is closed and SHOW_ALL_ROUNDS is False so don't include this round in results
            continue

        summary = RoundSummary(
            is_assessment_active_status=assessment_active,
            is_round_open_status=round_open,
            is_not_yet_open_status=not_yet_open,
            fund_id=fund.id,
            round_id=round.id,
            fund_name=fund.name,
            round_name=round.title,
            assessment_stats=application_stats,
            assessments_href=url_for(
                "assessment_bp.fund_dashboard",
                fund_short_name=fund.short_name,
                round_short_name=round.short_name.lower(),
            ),
            access_controller=access_controller,
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
            sorting_date=sorting_date,
        )
        round_id_to_summary_map[round.id] = summary
        summaries.append(summary)

    if live_rounds:
        live_rounds_map = {r.id: r for r in live_rounds}
        round_stats = get_application_stats(
            [fund.id], [r.id for r in live_rounds]
        )
        this_fund_stats = next(
            f for f in round_stats["metrics"] if f["fund_id"] == fund.id
        )
        for this_round_stats in this_fund_stats["rounds"]:
            current_round_id = this_round_stats["round_id"]
            if current_round_id not in live_rounds_map:
                continue

            statuses = this_round_stats["application_statuses"]
            live_round = live_rounds_map[current_round_id]
            round_id_to_summary_map[
                current_round_id
            ].live_round_stats = LiveRoundStats(
                closing_date=live_round.deadline,
                not_started=statuses["NOT_STARTED"],
                in_progress=statuses["IN_PROGRESS"],
                completed=statuses["COMPLETED"],
                submitted=statuses["SUBMITTED"],
            )

    return sorted(summaries, key=lambda s: s.sorting_date, reverse=True)


def is_after_today(date_str: str):
    """Check if the provided datetime string has passed the current datetime"""
    uk_tz = pytz.timezone("Europe/London")
    date_format = "%Y-%m-%dT%H:%M:%S"
    dt = datetime.datetime.strptime(date_str, date_format)
    dt_uk = uk_tz.localize(dt)
    now_uk = datetime.datetime.now(tz=uk_tz)
    return dt_uk > now_uk
