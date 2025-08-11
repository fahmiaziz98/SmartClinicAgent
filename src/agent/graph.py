
from langsmith import Client
from typing import Any, Callable, List

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition

from src.agent.setting import settings
from src.agent.prompt import patient_agent_prompt
from src.agent.tools_calendar import (
    get_doctor_schedule_appointments,
    get_event_by_id,
    create_doctor_appointment,
    update_doctor_appointment,
    cancel_doctor_appointment,
)
from src.agent.tool_retriever import knowledge_base_tool


_ = Client()

llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL_PRO,
    api_key=settings.GEMINI_API_KEY,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
)

TOOLS: List[Callable[..., Any]] = [
    get_doctor_schedule_appointments,
    get_event_by_id,
    knowledge_base_tool,

    # sensitif tools
    create_doctor_appointment,
    update_doctor_appointment,
    cancel_doctor_appointment,
]