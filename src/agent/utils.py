import pytz
from datetime import datetime
from typing import Annotated, Dict
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode


def format_event(event: Dict) -> Dict:
    """
    Format event details for patient display:
    - Shows only date, start/end time, and duration
    - Localized to Asia/Jakarta timezone
    - Omits unnecessary internal details
    """
    tz = pytz.timezone('Asia/Jakarta')

    start = event.get('start', {})
    end = event.get('end', {})
    all_day = False

    if 'dateTime' in start:
        start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00')).astimezone(tz)
        end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00')).astimezone(tz)
    elif 'date' in start:
        start_time = datetime.fromisoformat(start['date'])
        end_time = datetime.fromisoformat(end['date'])
        all_day = True
    else:
        start_time = None
        end_time = None

    duration_minutes = None
    if start_time and end_time:
        duration_minutes = int((end_time - start_time).total_seconds() / 60)

    return {
        'date': start_time.strftime('%d %B %Y') if start_time else '',
        'start_time': start_time.strftime('%H:%M') if start_time else '',
        'end_time': end_time.strftime('%H:%M') if end_time else '',
        'duration_minutes': duration_minutes,
        'all_day': all_day
    }

def handle_tool_error(state: State) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n Please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }

def create_tool_node_with_fallback(tools: list) -> dict:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )