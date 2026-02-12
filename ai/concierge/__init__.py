"""
AI Concierge — RAG chatbot with 3-tier memory for Gateway El Salvador.

Public API::

    from ai.concierge import Concierge, ConciergeConfig

    config = ConciergeConfig(anthropic_api_key="sk-...")
    concierge = Concierge(config)
    await concierge.initialize()

    result = await concierge.chat("Tell me about La Libertad", user_id="u123")
"""

from .concierge import Concierge, ConciergeConfig
from .memory import ConversationMemory, MemoryConfig
from .models import (
    ChatMessage,
    ConversationSummary,
    FactCategory,
    MemorySnapshot,
    MessageRole,
    RetrievedChunk,
    UserFact,
)

__all__ = [
    "Concierge",
    "ConciergeConfig",
    "ConversationMemory",
    "MemoryConfig",
    "ChatMessage",
    "ConversationSummary",
    "FactCategory",
    "MemorySnapshot",
    "MessageRole",
    "RetrievedChunk",
    "UserFact",
]
