"""Context configuration for the agent.

This module defines the `Context` class which provides system prompts
and model configuration for the agent. It is built on top of Pydantic's BaseModel
to validate and manage agent context settings.
"""

from __future__ import annotations

import os

from pydantic import BaseModel, ConfigDict, Field

from .prompt import SYSTEM_PROMPT, SYSTEM_PROMPT_MEM0


class Context(BaseModel):
    """The context for the agent."""

    system_prompt: str = Field(
        default_factory=lambda: SYSTEM_PROMPT,
        description="System prompt that sets the agent's behavior.",
    )
    system_prompt_mem0: str = Field(
        default_factory=lambda: SYSTEM_PROMPT_MEM0,
        description="Add a system prompt when saving the coversation history to better understand the context.",
    )
    model: str = Field(
        default_factory=lambda: os.getenv("MODEL", "google_genai/gemini-2.5-flash"),
        description="Provider/model name, e.g. provider/model-name.",
    )

    # Terima field ekstra seperti 'host' tanpa error
    model_config = ConfigDict(extra="allow")
