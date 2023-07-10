from dataclasses import dataclass
from typing import List

from app.assess.models.flag_v2 import FlagTypeV2
from app.assess.models.flag_v2 import FlagV2

# TODO : Check if there is better way to do it?


@dataclass
class TeamFlagStats:
    team_name: str
    num_of_flags: int
    num_of_resolved: int
    num_of_raised: int
    num_of_stopped: int
    ordinal_list: list
    flags_list: List[FlagV2]


@dataclass
class TeamsFlagData:
    teams_stats: dict

    @classmethod
    def from_flags(cls, flags_list: List[FlagV2], teams_list: list = None):
        teams_stats = {}
        ordinal_list = [
            "First",
            "Second",
            "Third",
            "Fourth",
            "Fifth",
        ]  # assume max 5 flags/team
        if isinstance(flags_list, FlagV2):
            flags_list = [flags_list]

        if not teams_list:
            teams_list = [flag.latest_allocation for flag in flags_list]
            teams_list = list(
                set(teams_list) - set([None])
            )  # filter for unique teams

        for team in teams_list:
            num_of_flags = 0
            num_of_resolved = 0
            num_of_raised = 0
            num_of_stopped = 0
            team_flags_list = []
            # ordinal_list = []

            for flag in flags_list:
                if flag.latest_allocation == team:
                    num_of_flags = num_of_flags + 1
                    team_flags_list.append(flag)
                    # ordinal_list.append(TeamsFlagData.ordinal(num_of_flags))
                    if flag.latest_status == FlagTypeV2.RAISED:
                        num_of_raised = num_of_raised + 1
                    elif flag.latest_status == FlagTypeV2.RESOLVED:
                        num_of_resolved = num_of_resolved + 1
                    elif flag.latest_status == FlagTypeV2.STOPPED:
                        num_of_stopped = num_of_stopped + 1

            teams_stats[team] = TeamFlagStats(
                team_name=team,
                num_of_flags=num_of_flags,
                num_of_resolved=num_of_resolved,
                num_of_raised=num_of_raised,
                num_of_stopped=num_of_stopped,
                ordinal_list=ordinal_list[0:num_of_flags][::-1],
                flags_list=team_flags_list[::-1],
            )

        return cls(teams_stats=teams_stats)

    @staticmethod
    def ordinal(n: int):
        if 11 <= (n % 100) <= 13:
            suffix = "th"
        else:
            suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
        return str(n) + suffix
