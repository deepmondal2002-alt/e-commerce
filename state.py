from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class SchedulingState(TypedDict):
    messages: Annotated[list, add_messages]
