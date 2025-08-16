"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""
import pytz
from loguru import logger
from datetime import datetime
from typing import Dict, List, Literal, cast

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime

from src.agent.context import Context
from src.agent.state import State, InputState
from src.agent.tools import TOOLS_CALENDAR, TOOLS_KNOWLEDGE_BASE
from src.agent.utils import create_tool_node_with_fallback, load_chat_model



async def call_model(
    state: State,
    runtime: Runtime[Context]
) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our "agent".

    This function prepares the prompt, initializes the model, and processes the response.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    # get timezone
    logger.info("Call agent...")
    tz = pytz.timezone("Asia/Jakarta")

    model = load_chat_model(runtime.context.model).bind_tools(TOOLS_KNOWLEDGE_BASE + TOOLS_CALENDAR)

    # Format the system prompt. Customize this to change the agent's behavior.
    system_message = runtime.context.system_prompt.format(
        time=datetime.now(tz=tz).isoformat()
    )

    # Get the model's response
    response = cast(
        AIMessage,
        await model.ainvoke(
            [{"role": "system", "content": system_message}, *state.messages]
        ),
    )

    # Handle the case when it's the last step and the model still wants to use a tool
    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    # Return the model's response as a list to be added to existing messages
    return {"messages": [response]}


def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """Determine the next node based on the model's output.

    This function checks if the model's last message contains tool calls.

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call ("__end__" or "tools").
    """
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


# Define graph
builder = StateGraph(State, input_schema=InputState, context_schema=Context)
builder.add_node("call_model", call_model)
builder.add_node("tools", ToolNode(TOOLS_KNOWLEDGE_BASE + TOOLS_CALENDAR))

# Set the entrypoint as `call_model`
# This means that this node is the first one called
builder.add_edge("__start__", "call_model")

# Add a conditional edge to determine the next step after `call_model`
builder.add_conditional_edges(
    "call_model",
    # After call_model finishes running, the next node(s) are scheduled
    # based on the output from route_model_output
    route_model_output,
)

# Add a normal edge from `tools` to `call_model`
# This creates a cycle: after using tools, we always return to the model
builder.add_edge("tools", "call_model")

# Compile the builder into an executable graph
graph = builder.compile(name="ReAct Agent")
