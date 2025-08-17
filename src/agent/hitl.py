"""Human-in-the-loop (HITL) wrapper for LangGraph tools."""

from typing import Callable, Optional, Union

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from langchain_core.tools import tool as create_tool
from langgraph.prebuilt.interrupt import (
    ActionRequest,
    HumanInterrupt,
    HumanInterruptConfig,
)
from langgraph.types import interrupt
from loguru import logger


def human_in_the_loop(
    tool: Union[Callable, BaseTool],
    *,
    interrupt_config: Optional[HumanInterruptConfig] = None,
) -> BaseTool:
    """
    Wrap a tool with human-in-the-loop (HITL) functionality.

    Args:
        tool (Callable | BaseTool): The tool to wrap.
        interrupt_config (HumanInterruptConfig, optional):
            Configuration for human interrupt. Defaults to a safe config.

    Returns:
        BaseTool: A wrapped tool with HITL review support.
    """
    if not isinstance(tool, BaseTool):
        tool = create_tool(tool)

    if interrupt_config is None:
        interrupt_config = HumanInterruptConfig(
            allow_ignore=False,  # Disallow skipping this step
            allow_respond=True,  # Allow text feedback
            allow_edit=True,  # Allow editing
            allow_accept=True,  # Allow direct acceptance
        )

    @create_tool(
        tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
    )
    def call_tool_with_interrupt(config: RunnableConfig, **tool_input):
        logger.info(f"Using interrupt tool {tool.name}")
        request = HumanInterrupt(
            action_request=ActionRequest(
                action=tool.name,  # The action being requested
                args=tool_input,  # Arguments for the action
            ),
            config=interrupt_config,
            description="Please review the command before execution",
        )

        response = interrupt([request])[0]

        if response["type"] == "accept":
            tool_response = tool.invoke(tool_input, config)
            logger.success(f"Accepted tool: {tool.name}")

        elif response["type"] == "edit":
            tool_input = response["args"]["args"]
            tool_response = tool.invoke(tool_input, config)
            logger.success(f"Edited tool args for: {tool.name}")

        elif response["type"] == "response":
            tool_response = response["args"]
            logger.success(f"User feedback captured for: {tool.name}")

        else:
            logger.error(f"Unsupported interrupt response type: {response['type']}")
            raise ValueError(f"Unsupported interrupt response type: {response['type']}")

        return tool_response

    return call_tool_with_interrupt
