import pytz
from datetime import datetime
from typing import Any, Dict, List

from googleapiclient.errors import HttpError
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode

from src.agent.core import CALENDAR_SERVICE
from src.agent.setting import settings


def create_event(
    title: str,
    start_datetime: datetime,
    end_datetime: datetime,
    description: str = '',
    location: str = '',
    timezone: str = 'Asia/Jakarta'
) -> Dict[str, Any]:
    """
    Creates a new event in Google Calendar.

    This function constructs and executes a request to the Google Calendar API
    to create a new event with the provided details.

    Args:
        title: The title of the event.
        start_datetime: The start date and time of the event.
        end_datetime: The end date and time of the event.
        description: An optional description for the event.
        location: An optional location for the event.
        timezone: The timezone for the event's start and end times.

    Returns:
        A dictionary containing the operation status and event details:
        - success (bool): True if the event was created successfully, False otherwise.
        - event (Dict | None): Formatted details of the created event, or None on failure.
        - event_id (str | None): The unique ID of the created event, or None on failure.
        - message (str): A status message describing the outcome.
    """
    try:
        tz = pytz.timezone(timezone)
        start_datetime = tz.localize(start_datetime)
        end_datetime = tz.localize(end_datetime)

        event_body = {
            'summary': title,
            'description': description,
            'location': location,
            'start': {'dateTime': start_datetime.isoformat(), 'timeZone': timezone},
            'end': {'dateTime': end_datetime.isoformat(), 'timeZone': timezone},
        }

        event = CALENDAR_SERVICE.events().insert(
            calendarId=settings.CALENDAR_ID,
            body=event_body
        ).execute()

        formatted_event = format_event_details(event)

        return {
            'success': True,
            'event': formatted_event,
            'event_id': event.get('id'),
            'message': f'Event "{title}" was created successfully.'
        }

    except HttpError as error:
        return {
            'success': False,
            'event': None,
            'event_id': None,
            'message': f'An error occurred while creating the event: {error}'
        }
    
def format_event_details(event: Dict) -> Dict:
    """
    Formats raw event data from Google Calendar API into a structured dictionary.

    Args:
        event: The raw event dictionary from the Google Calendar API.

    Returns:
        A dictionary with formatted, easy-to-access event details.
    """
    start = event.get('start', {})
    end = event.get('end', {})

    start_time = None
    end_time = None
    all_day = False

    if 'dateTime' in start:
        start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
    elif 'date' in start:
        start_time = datetime.fromisoformat(start['date'])
        end_time = datetime.fromisoformat(end['date'])
        all_day = True


    return {
        'id': event.get('id'),
        'title': event.get('summary', 'No Title'),
        'description': event.get('description', ''),
        'location': event.get('location', ''),
        'start_time': start_time,
        'end_time': end_time,
        'all_day': all_day,
        'creator': event.get('creator', {}).get('email', ''),
        'status': event.get('status', '')
    }

def format_event(event: Dict) -> Dict:
    """
    Formats event details for a user-friendly display, localized to a specific timezone.

    This function simplifies the event data to show only essential information for a patient,
    such as date, time, and duration, converted to the 'Asia/Jakarta' timezone.

    Args:
        event: The raw event dictionary from the Google Calendar API.

    Returns:
        A simplified dictionary containing the event's date, start time, end time,
        duration in minutes, and an all-day flag.
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

def handle_tool_error(state: dict) -> dict:
    """
    A fallback function to handle errors that occur within a ToolNode.

    It captures the error and formats it into a ToolMessage, allowing the
    agent to understand that the tool call failed and why.

    Args:
        state: The current state of the graph, which includes the error information.

    Returns:
        A dictionary with a "messages" key containing a list of ToolMessages
        reporting the error.
    """
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
    """
    Creates a ToolNode for a LangGraph agent with a built-in error fallback mechanism.

    If any tool in the node raises an exception, the `handle_tool_error` function
    will be invoked to process the error gracefully.

    Args:
        tools: A list of tools to be included in the ToolNode.

    Returns:
        A ToolNode instance configured with an error fallback.
    """
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )