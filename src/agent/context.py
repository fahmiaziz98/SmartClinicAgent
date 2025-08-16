from __future__ import annotations

import os
from pydantic import BaseModel, Field, ConfigDict
from . import prompt

class Context(BaseModel):
    """The context for the agent."""

    system_prompt: str = Field(
        default_factory=lambda: prompt.SYSTEM_PROMPT,
        description="System prompt that sets the agent's behavior.",
    )
    model: str = Field(
        default_factory=lambda: os.getenv("MODEL", "google_genai/gemini-2.5-flash"),
        description="Provider/model name, e.g. provider/model-name.",
    )

    # Terima field ekstra seperti 'host' tanpa error
    model_config = ConfigDict(extra="allow")
