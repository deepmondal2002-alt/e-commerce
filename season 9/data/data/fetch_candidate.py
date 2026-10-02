from mcp_tool import get_client, tools_session, parse_tool_result
from state import SchedulingState


async def fetch_candidates_and_panel(state: SchedulingState) -> dict:
    """Look up candidates ready for scheduling for the given job_id.

    Pure tools calls, no LLM reasoning needed here.
    """
    client = get_client()

    async with tools_session(client, "ats") as tools:
        tools_by_name = {tool.name: tool for tool in tools}

    candidates_raw = await tools_by_name["get_candidates_ready_for_scheduling"].ainvoke(
        {"job_id": state["job_id"]}
    )
    candidates = parse_tool_result(candidates_raw)

    if not candidates:
        raise ValueError(
            f"No candidates ready for scheduling for job_id={state['job_id']}"
        )

    candidate = candidates[0]

    panel_raw = await tools_by_name["get_panel"].ainvoke({"job_id": state["job_id"]})
    panel = parse_tool_result(panel_raw)
    
    return {
        "candidates": candidates,
        "panel": panel,
        "status" :"checking_availability"
    }