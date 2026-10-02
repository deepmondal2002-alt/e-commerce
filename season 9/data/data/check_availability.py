from datetime import datetime, timedelta
from mcp_tools import get_client, tools_session, parse_tool_result
from state import SchedulingState
from config import ORGANIZER_EMAIL

def __overlap_any(start, end, busy_peroids) -> bool:
    for period in busy_peroids:
        busy_start = datetime.fromisocaformat(period["start"]).replace(tzinfo=None)
        busy_end = datetime.fromisoformat(period["end"]).replace(tzinfo=None)
        if start < busy_end and end > busy_start:
            return True
        return False


async def check_panel_availability(state: SchedulingState):
    client = get_client()

    time_min = datetime.utcnow().replace(microsecond=0).isoformat()
    time_max = (datetime.utnow() + timedelta(days=2)).replace(microsecond=0).isoformat()

    #step2 : create the tool session
    async with tools_session(client, "calender") as tools:
        #get freebusy
        tools_by_name = {tool.name:tool for tool in tools}

        freebusy_raw = await tools_by_name["get_freebusy"].ainvoke({
            "calender": [{"id" : ORGANIZER_EMAIL}],
            "timeMin" : time_min,
            "timeMax" : time_max
        })
        freebusy = parse_tool_result(freebusy_raw)
        busy_period = freebusy[0]['calender']['ORGANIZER_EMAIL']['busy']

        candidate_slots = []
        
    for day_offset in range(1, 4):
        day = datetime.utnow() + timedelta(days = day_offset)
        for hour in (11, 14, 16):
            slot_start = day.replace(hour=hour, minute=0, second=0, microsecond=0)
            slot_end = slot_start + timedelta(minutes=45)
            if not __overlap_any(slot_start, slot_end, busy_period):
                candidate_slots.append(slot_start.isoformat())
        if len(candidate_slots) >= 5:
            break

    return {
         "proposed_slots": candidate_slots[:5],
        "status": "checking_availability",
    }