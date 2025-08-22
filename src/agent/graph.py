"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Literal, cast

import pytz
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime
from loguru import logger

from src.agent.context import Context
from src.agent.memory import save_memory_background, search_memory
from src.agent.state import InputState, State
from src.agent.tools import TOOLS_CALENDAR, TOOLS_KNOWLEDGE_BASE
from src.agent.utils import get_message_text, load_chat_model, task_done_callback

logger.add("logger.log", rotation="10 MB", retention="10 days", level="DEBUG")


async def call_model(
    state: State,
    config: RunnableConfig,
    runtime: Runtime[Context],
) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our agent."""
    logger.info("Call agent...")
    tz = pytz.timezone("Asia/Jakarta")

    # get messages from state
    messages = state.messages
    user_id = config["configurable"]["thread_id"]
    user_message = get_message_text(messages[-1])

    context = await search_memory(
        query=user_message,
        user_id=user_id,
    )

    model = load_chat_model(runtime.context.model).bind_tools(TOOLS_KNOWLEDGE_BASE + TOOLS_CALENDAR)

    system_message = runtime.context.system_prompt.format(
        time=datetime.now(tz=tz).strftime("%Y-%m-%d %H:%M:%S"),
        conversation_history=context,
    )

    response = cast(
        AIMessage,
        await model.ainvoke(
            [{"role": "system", "content": system_message}, *messages],
        ),
    )

    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content=("Sorry, I could not find an answer to your question in the specified number of steps."),
                )
            ]
        }

    if not response.tool_calls and response.content:
        metadata = {"timestamp": datetime.now(tz=tz).strftime("%Y-%m-%d %H:%M:%S")}

        conversation = [
            {"role": "system", "content": runtime.context.system_prompt_mem0},
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": response.content},
        ]

        task = asyncio.create_task(save_memory_background(conversation, user_id, metadata))

        task.add_done_callback(task_done_callback)

    return {"messages": [response]}


def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """Determine the next node based on the model's output."""
    logger.info("Route agent...")
    last_messages = state.messages[-1]
    if not isinstance(last_messages, AIMessage):
        raise ValueError(f"Expected AIMessage in output edges, but got {type(last_messages).__name__}")
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
