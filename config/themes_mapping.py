def ordered_themes(fund_round_short_name):

    if fund_round_short_name == "COF-EOIR1":
        return [
            "organisation-details",
            "about-your-asset",
            "your-funding-request",
            "development-support-provider",
        ]

    if fund_round_short_name in [
        "COFR3W2",
        "COFR3W1",
        "COFR3W3",
        "COFR2W3",
        "COFR2W2",
        "COFR4W1",
        "COFR4W2",
    ]:
        return [
            (
                "general_info"
                if fund_round_short_name in ["COFR2W3", "COFR2W2"]
                else "general_information"
            ),
            "activities",
            "partnerships",
            "contact_information",
            "previous_funding",
            "project_summary",
            "asset_ownership",
            "asset_evidence",
            "asset_background",
            "asset_location",
            "business_plan",
            "declarations",
            (
                "project_qualification"
                if fund_round_short_name in ["COFR2W3", "COFR2W2"]
                else None
            ),
            (
                None
                if fund_round_short_name in ["COFR4W1", "COFR4W2"]
                else "subsidy_control_and_state_aid"
            ),
            (
                "community_use/significance"
                if fund_round_short_name in ["COFR4W1", "COFR4W2"]
                else "community_use"
            ),
            "risk_and_impact_of_loss",
            "engaging-the-community",
            "local-support",
            (
                None
                if fund_round_short_name in ["COFR2W3", "COFR2W2"]
                else "delivering_and_sustaining_benefits"
            ),
            (
                None
                if fund_round_short_name in ["COFR2W3", "COFR2W2"]
                else "benefitting_the_whole_community"
            ),
            "environmental-considerations",
            "funding_requested",
            (
                "feasibility"
                if fund_round_short_name in ["COFR2W3", "COFR2W2"]
                else "feasiblilty"
            ),
            "risk",
            (
                "income_and_running_costs"
                if fund_round_short_name in ["COFR2W3", "COFR2W2"]
                else "income_&_running_costs"
            ),
            "previous_experience",
            "governance_and_structures",
            "recruitment",
            "representing_community_views",
            "accessibility_and_inclusivity",
            (
                "delivering_and_sustaining_benefits"
                if fund_round_short_name in ["COFR2W3", "COFR2W2"]
                else None
            ),
            (
                "benefitting_the_whole_community"
                if fund_round_short_name in ["COFR2W3", "COFR2W2"]
                else None
            ),
            (
                "addressing_community_challenges"
                if fund_round_short_name in ["COFR2W3", "COFR2W2"]
                else None
            ),
        ]

    if fund_round_short_name == "DPIFR2":
        return [
            "about_your_organisation",
            "future_work",
            "declarations",
            "your_skills_and_experience",
            "roles_and_recruitment",
            "engaging_the_ODP_community",
            "engaging_the_organisation",
            "dataset_information",
        ]

    if fund_round_short_name == "NSTFR2":
        return [
            "organisation_information",
            "organisation-type",
            "application_information",
            "joint_applications",
            "declarations",
            "staff_and_volunteers",
            "current_service",
            "targeted_criteria_current",
            "proposal_summary",
            "milestones",
            "your_local_area_need",
            "proposed_services",
            "targeted_criteria_proposed",
            "working_in_partnership",
            "proposal_sustainability",
            "proposal_support",
            "restricted_eligibility",
            "risk_to_the_proposal",
            "funding_required",
            "building_works",
            "match_funding",
        ]

    if fund_round_short_name == "CYPR1":
        return [
            "organisation-name-and-address",
            "organisation-classification",
            "partner-organisation",
            "applicant-information",
            "declarations",
            "your-skills-and-experience",
            "outputs",
            "outcome",
            "existing-work",
            "project-milestones",
            "objectives-and-activities",
            "location-of-activities",
            "working-with-fund-beneficiaries",
            "risk-and-deliverability",
            "value-for-money",
        ]
    if fund_round_short_name == "HSRA":
        return [
            "total_expected_cost",
            "refurbishment_costs",
            "other_costs",
            "vacant_property_details",
            "designated_area_details",
            "milestones",
        ]
