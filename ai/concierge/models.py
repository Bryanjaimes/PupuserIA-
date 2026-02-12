"""
Memory Models — Data structures for the 3-tier conversation memory system.
===========================================================================

Tier 1 — Working Memory  (Redis):  Current session messages, ephemeral context
Tier 2 — Episodic Memory (PostgreSQL):  User facts, preferences, conversation summaries
Tier 3 — Semantic Memory (Pinecone):  Knowledge-base chunks retrieved via embedding similarity
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4


# ── Enums ────────────────────────────────────────────


class FactCategory(str, Enum):
    """Categories of extracted user facts."""

    PREFERENCE = "preference"          # "prefers beach properties"
    BUDGET = "budget"                  # "budget is $150K–200K"
    TIMELINE = "timeline"              # "planning to visit in March"
    LOCATION_INTEREST = "location"     # "interested in La Libertad"
    PERSONAL = "personal"              # "retiring in 2 years"
    INVESTMENT_GOAL = "investment"     # "looking for rental yield"
    LANGUAGE = "language"              # "prefers Spanish"
    TRAVEL = "travel"                  # "traveling with family of 4"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ── Working Memory (Tier 1 — Redis) ─────────────────


@dataclass
class ChatMessage:
    """A single message in a conversation."""

    role: MessageRole
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    message_id: str = field(default_factory=lambda: uuid4().hex[:12])
    metadata: dict = field(default_factory=dict)

    def to_api_message(self) -> dict:
        """Convert to the format expected by the Anthropic API."""
        return {"role": self.role.value, "content": self.content}

    def to_dict(self) -> dict:
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "message_id": self.message_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ChatMessage:
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=data.get("timestamp", ""),
            message_id=data.get("message_id", uuid4().hex[:12]),
            metadata=data.get("metadata", {}),
        )


# ── Episodic Memory (Tier 2 — PostgreSQL) ───────────


@dataclass
class UserFact:
    """
    A single extracted fact about a user.

    Facts are extracted from conversations by an LLM pass
    and stored in PostgreSQL for cross-session retrieval.
    """

    fact_id: str = field(default_factory=lambda: uuid4().hex)
    user_id: str = ""
    category: FactCategory = FactCategory.PREFERENCE
    content: str = ""                         # natural-language fact
    confidence: float = 0.9                   # 0.0–1.0
    source_conversation_id: str = ""          # which conversation it came from
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    is_active: bool = True                    # soft-delete for corrections

    def to_dict(self) -> dict:
        return {
            "fact_id": self.fact_id,
            "user_id": self.user_id,
            "category": self.category.value,
            "content": self.content,
            "confidence": self.confidence,
            "source_conversation_id": self.source_conversation_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> UserFact:
        return cls(
            fact_id=data.get("fact_id", uuid4().hex),
            user_id=data.get("user_id", ""),
            category=FactCategory(data.get("category", "preference")),
            content=data.get("content", ""),
            confidence=data.get("confidence", 0.9),
            source_conversation_id=data.get("source_conversation_id", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            is_active=data.get("is_active", True),
        )


@dataclass
class ConversationSummary:
    """
    Compressed summary of a completed conversation.

    When a conversation exceeds the working-memory window or ends,
    the full history is summarized into a paragraph and stored here.
    This is cheaper to retrieve than replaying 50+ messages.
    """

    summary_id: str = field(default_factory=lambda: uuid4().hex)
    user_id: str = ""
    conversation_id: str = ""
    summary: str = ""                         # 1-2 paragraph natural-language summary
    topics: list[str] = field(default_factory=list)  # e.g. ["beach property", "La Libertad"]
    message_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "summary_id": self.summary_id,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "summary": self.summary,
            "topics": self.topics,
            "message_count": self.message_count,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ConversationSummary:
        return cls(
            summary_id=data.get("summary_id", uuid4().hex),
            user_id=data.get("user_id", ""),
            conversation_id=data.get("conversation_id", ""),
            summary=data.get("summary", ""),
            topics=data.get("topics", []),
            message_count=data.get("message_count", 0),
            created_at=data.get("created_at", ""),
        )


# ── Semantic Memory (Tier 3 — Pinecone) ─────────────


@dataclass
class RetrievedChunk:
    """A chunk of knowledge retrieved from the vector store."""

    chunk_id: str
    content: str
    source: str                                # e.g. "guide:la-libertad-beaches"
    score: float                               # cosine similarity
    metadata: dict = field(default_factory=dict)

    def to_context_string(self) -> str:
        """Format for injection into the LLM prompt."""
        return f"[Source: {self.source} | Relevance: {self.score:.2f}]\n{self.content}"


# ── Composite Memory Snapshot ────────────────────────


@dataclass
class MemorySnapshot:
    """
    Everything the Concierge remembers about a user at inference time.

    This is the assembled context passed alongside the user's message
    when building the Claude prompt.
    """

    # Tier 1 — Working
    recent_messages: list[ChatMessage] = field(default_factory=list)

    # Tier 2 — Episodic
    user_facts: list[UserFact] = field(default_factory=list)
    past_summaries: list[ConversationSummary] = field(default_factory=list)

    # Tier 3 — Semantic
    knowledge_chunks: list[RetrievedChunk] = field(default_factory=list)

    def format_episodic_context(self) -> str:
        """Render episodic memory as a context block for the prompt."""
        if not self.user_facts and not self.past_summaries:
            return ""

        parts: list[str] = []

        if self.user_facts:
            facts_text = "\n".join(
                f"- [{f.category.value}] {f.content}" for f in self.user_facts if f.is_active
            )
            parts.append(f"## What you know about this user\n{facts_text}")

        if self.past_summaries:
            # Include the 3 most recent summaries
            recent = sorted(self.past_summaries, key=lambda s: s.created_at, reverse=True)[:3]
            summaries_text = "\n\n".join(
                f"**Previous conversation ({s.created_at[:10]}):** {s.summary}" for s in recent
            )
            parts.append(f"## Previous conversations\n{summaries_text}")

        return "\n\n".join(parts)

    def format_semantic_context(self) -> str:
        """Render semantic memory as a context block for the prompt."""
        if not self.knowledge_chunks:
            return ""
        chunks_text = "\n\n---\n\n".join(c.to_context_string() for c in self.knowledge_chunks)
        return f"## Relevant knowledge\n{chunks_text}"
