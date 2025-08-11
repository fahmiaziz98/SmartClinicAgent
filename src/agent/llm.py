from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
from src.agent.setting import settings


LLM : ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL_PRO,
    api_key=settings.GEMINI_API_KEY,
    temperature=settings.TEMPERATURE,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
    convert_system_message_to_human=True,
)