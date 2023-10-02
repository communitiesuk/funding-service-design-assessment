from app.blueprints.services.data_services import get_assessor_task_list_state
from app.blueprints.services.data_services import get_fund
from app.blueprints.services.data_services import get_round
from app.blueprints.services.models.assessor_task_list import AssessorTaskList


def get_state_for_tasklist_banner(application_id) -> AssessorTaskList:
    assessor_task_list_metadata = get_assessor_task_list_state(application_id)
    fund = get_fund(assessor_task_list_metadata["fund_id"])
    round = get_round(
        assessor_task_list_metadata["fund_id"],
        assessor_task_list_metadata["round_id"],
    )
    assessor_task_list_metadata["fund_name"] = fund.name
    assessor_task_list_metadata["fund_short_name"] = fund.short_name
    assessor_task_list_metadata["round_short_name"] = round.short_name
    assessor_task_list_metadata["fund_guidance_url"] = round.guidance_url
    state = AssessorTaskList.from_json(assessor_task_list_metadata)
    return state
