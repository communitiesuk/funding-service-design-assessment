import datetime
from dataclasses import dataclass

import pytz
from app.assess.data import get_assessments_stats
from app.assess.data import get_rounds
from app.assess.models.fund import Fund
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
    name: str
    is_active_status: bool
    application_stats: Stats
    assessments_href: str


def create_fund_summaries(fund: Fund) -> list[FundSummary]:
    """Get all the round stats in a fund."""
    summaries = []
    for round in get_rounds(fund.id):
        # only show closed rounds in assessment
        if not is_after_today(round.deadline):
            round_stats = get_assessments_stats(fund.id, round.id)
            summary = FundSummary(
                name=round.title,
                is_active_status=is_after_today(round.assessment_deadline),
                application_stats=Stats(
                    date=round.assessment_deadline,
                    total_received=round_stats["total"],
                    completed=round_stats["completed"],
                    started=round_stats["assessing"],
                    qa_complete=round_stats["qa_completed"],
                    stopped=round_stats["stopped"],
                ),
                assessments_href=url_for(
                    "assess_bp.fund_dashboard",
                    fund_short_name=fund.short_name.lower(),
                    round_short_name=round.short_name.lower(),
                ),
            )
            summaries.append(summary)
    return summaries


def is_after_today(date_str: str):
    """Check if the provided datetime string has passed the current datetime"""
    uk_tz = pytz.timezone("Europe/London")
    date_format = "%Y-%m-%dT%H:%M:%S"
    dt = datetime.datetime.strptime(date_str, date_format)
    dt_uk = uk_tz.localize(dt)
    now_uk = datetime.datetime.now(tz=uk_tz)
    return dt_uk > now_uk
