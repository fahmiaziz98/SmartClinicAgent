"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

from datetime import datetime
from typing import Dict, List, Literal, cast

import pytz
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime
from loguru import logger

from src.agent.context import Context
from src.agent.state import InputState, State
from src.agent.tools import TOOLS_CALENDAR, TOOLS_KNOWLEDGE_BASE
from src.agent.utils import load_chat_model


async def call_model(
    state: State,
    runtime: Runtime[Context],
) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our agent."""
    logger.info("Call agent...")
    tz = pytz.timezone("Asia/Jakarta")

    model = load_chat_model(runtime.context.model).bind_tools(
        TOOLS_KNOWLEDGE_BASE + TOOLS_CALENDAR
    )

    system_message = runtime.context.system_prompt.format(
        time=datetime.now(tz=tz).isoformat()
    )

    response = cast(
        AIMessage,
        await model.ainvoke(
            [{"role": "system", "content": system_message}, *state.messages],
        ),
    )

    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content=(
                        "Sorry, I could not find an answer to your question "
                        "in the specified number of steps."
                    ),
                )
            ]
        }

    return {"messages": [response]}


def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """Determine the next node based on the model's output."""
    logger.info("Route agent...")
    last_messages = state.messages[-1]
    if not isinstance(last_messages, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_messages).__name__}"
        )
    if not last_messages.tool_calls:
        logger.info("Route agent to `__end__`")
        return "__end__"

    logger.info("Route agent to `tools`")
    return "tools"


builder = StateGraph(State, input_schema=InputState, context_schema=Context)
builder.add_node("call_model", call_model)
builder.add_node("tools", ToolNode(TOOLS_KNOWLEDGE_BASE + TOOLS_CALENDAR))

builder.add_edge("__start__", "call_model")
builder.add_conditional_edges("call_model", route_model_output)
builder.add_edge("tools", "call_model")

graph = builder.compile(name="ReAct Agent")
