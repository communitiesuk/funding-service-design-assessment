from app.assess.models.flag_teams import TeamsFlagData
from app.assess.models.flag_v2 import FlagV2


class TestTeamsFlagData:
    @staticmethod
    def create_flag(
        id,
        sections_to_flag,
        latest_status,
        latest_allocation,
        application_id,
        updates,
    ):
        return FlagV2(
            id=id,
            sections_to_flag=sections_to_flag,
            latest_status=latest_status,
            latest_allocation=latest_allocation,
            application_id=application_id,
            updates=updates,
        )

    def test_from_flags_with_empty_list(self):
        teams_data = TeamsFlagData.from_flags([])
        assert teams_data.teams_stats == {}

    def test_from_flags_with_single_flag(self):
        flag = self.create_flag(
            "1", ["section1", "section2"], "RAISED", "TeamA", "AppA", []
        )
        teams_data = TeamsFlagData.from_flags([flag])
        assert len(teams_data.teams_stats) == 1
        assert teams_data.teams_stats["TeamA"].num_of_flags == 1
        assert teams_data.teams_stats["TeamA"].num_of_raised == 1
        assert teams_data.teams_stats["TeamA"].num_of_resolved == 0
        assert teams_data.teams_stats["TeamA"].num_of_stopped == 0

    def test_from_flags_with_multiple_flags(self):
        flags = [
            self.create_flag(
                "1", ["section1", "section2"], "RAISED", "TeamA", "AppA", []
            ),
            self.create_flag(
                "2", ["section4", "section5"], "STOPPED", "TeamA", "AppC", []
            ),
            self.create_flag(
                "3", ["section7"], "RESOLVED", "TeamB", "AppE", []
            ),
            self.create_flag(
                "4", ["section10"], "RAISED", "TeamA", "AppH", []
            ),
            self.create_flag(
                "5", ["section11"], "RAISED", "TeamA", "AppI", []
            ),
            self.create_flag(
                "6", ["section12"], "RAISED", "TeamA", "AppJ", []
            ),
        ]
        teams_data = TeamsFlagData.from_flags(flags)
        assert len(teams_data.teams_stats) == 2
        assert teams_data.teams_stats["TeamA"].num_of_flags == 5
        assert teams_data.teams_stats["TeamA"].num_of_raised == 4
        assert teams_data.teams_stats["TeamA"].num_of_resolved == 0
        assert teams_data.teams_stats["TeamA"].num_of_stopped == 1

        # Check if the ordinals render correctly for the RAISED flags
        assert teams_data.teams_stats["TeamA"].ordinal_list == [
            "Fifth",
            "Fourth",
            "Third",
            "Second",
            "First",
        ]

        assert teams_data.teams_stats["TeamB"].num_of_flags == 1
        assert teams_data.teams_stats["TeamB"].num_of_raised == 0
        assert teams_data.teams_stats["TeamB"].num_of_resolved == 1
        assert teams_data.teams_stats["TeamB"].num_of_stopped == 0
        assert teams_data.teams_stats["TeamB"].ordinal_list == ["First"]
