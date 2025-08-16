"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

from datetime import UTC, datetime
from typing import Any, Callable, Dict, List, Literal, cast

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime

from agent.context import Context
from agent.hitl import human_in_the_loop
from agent.state import State, InputState
from agent.tools import (
    knowledge_base_tool,
    get_doctor_schedule_appointments,
    get_event_by_id,
    create_doctor_appointment,
    update_doctor_appointment,
    cancel_doctor_appointment
)
from agent.utils import create_tool_node_with_fallback, load_chat_model




async def call_model(
    state: State,
    runtime: Runtime[Context]
) -> Dict[str, List[AIMessage]]:
    pass

def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """Determine the next node based on the model's output.

    This function checks if the model's last message contains tool calls.

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call ("__end__" or "tools").
    """
    last_messages = state.messages[-1]
    if not isinstance(last_messages, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_messages).__name__}"
        )
    if not last_messages.tool_calls:
        return "__end__"
    return "tools"