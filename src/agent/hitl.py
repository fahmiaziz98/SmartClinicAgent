from loguru import logger
from typing import Callable
from langchain_core.tools import BaseTool, tool as create_tool
from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt
from langgraph.prebuilt.interrupt import HumanInterruptConfig, HumanInterrupt, ActionRequest


def human_in_the_loop(
    tool: Callable | BaseTool,
    *,
    interrupt_config: HumanInterruptConfig = None
):
    """Wrap a tool to support human-in-the-loop review."""
    if not isinstance(tool, BaseTool):
        tool = create_tool(tool)

    if interrupt_config is None:
        interrupt_config = HumanInterruptConfig(
            allow_ignore=False,    # Allow skipping this step
            allow_respond=True,   # Allow text feedback
            allow_edit=True,     # Don't allow editing
            allow_accept=True     # Allow direct acceptance
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
                args=tool_input  # Arguments for the action
            ),
            config=interrupt_config,
            description="Please review the command before execution"
        )

        response = interrupt([request])[0]
        # approve the tool call
        if response["type"] == "accept":
            tool_response = tool.invoke(tool_input, config)
            logger.success(f"Success accept tool: {tool.name}")
        # update tool call args
        elif response["type"] == "edit":
            tool_input = response["args"]["args"]
            tool_response = tool.invoke(tool_input, config)
            logger.success(f"Success edit tool: {tool.name}")
        # respond to the LLM with user feedback
        elif response["type"] == "response":
            user_feedback = response["args"]
            tool_response = user_feedback
            logger.success(f"Success feedback tool: {tool.name}")
        else:
            raise ValueError(f"Unsupported interrupt response type: {response['type']}")

        return tool_response



    return call_tool_with_interrupt