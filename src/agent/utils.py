"""Utility & helper functions."""

from datetime import datetime
from typing import Any, Dict, List

import pytz
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode


def format_event_details(event: Dict) -> Dict:
    """Format raw Google Calendar event data into structured details."""
    start = event.get("start", {})
    end = event.get("end", {})

    start_time = None
    end_time = None
    all_day = False

    if "dateTime" in start:
        start_time = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))
    elif "date" in start:
        start_time = datetime.fromisoformat(start["date"])
        end_time = datetime.fromisoformat(end["date"])
        all_day = True

    return {
        "id": event.get("id"),
        "title": event.get("summary", "No Title"),
        "description": event.get("description", ""),
        "location": event.get("location", ""),
        "start_time": start_time,
        "end_time": end_time,
        "all_day": all_day,
        "creator": event.get("creator", {}).get("email", ""),
        "status": event.get("status", ""),
    }


def format_event(event: Dict) -> Dict:
    """Format event details for user-friendly display (Asia/Jakarta timezone)."""
    tz = pytz.timezone("Asia/Jakarta")

    start = event.get("start", {})
    end = event.get("end", {})
    all_day = False

    if "dateTime" in start:
        start_time = datetime.fromisoformat(
            start["dateTime"].replace("Z", "+00:00")
        ).astimezone(tz)
        end_time = datetime.fromisoformat(
            end["dateTime"].replace("Z", "+00:00")
        ).astimezone(tz)
    elif "date" in start:
        start_time = datetime.fromisoformat(start["date"])
        end_time = datetime.fromisoformat(end["date"])
        all_day = True
    else:
        start_time = None
        end_time = None

    duration_minutes = None
    if start_time and end_time:
        duration_minutes = int((end_time - start_time).total_seconds() / 60)

    return {
        "date": start_time.strftime("%d %B %Y") if start_time else "",
        "start_time": start_time.strftime("%H:%M") if start_time else "",
        "end_time": end_time.strftime("%H:%M") if end_time else "",
        "duration_minutes": duration_minutes,
        "all_day": all_day,
    }


def handle_tool_error(state: dict) -> dict:
    """Fallback handler for errors in ToolNode."""
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\nPlease fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: List[Any]) -> ToolNode:
    """Create a ToolNode with built-in error fallback."""
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def get_message_text(msg: BaseMessage) -> str:
    """Extract plain text from a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    if isinstance(content, dict):
        return content.get("text", "")
    txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
    return "".join(txts).strip()


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name (provider/model)."""
    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(model, model_provider=provider)

