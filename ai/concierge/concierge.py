"""
AI Concierge — RAG-Powered Bilingual Chatbot with 3-Tier Memory
================================================================

Retrieval-Augmented Generation chatbot built on Claude API with
a proprietary knowledge base of El Salvador-specific content and
a persistent memory system that learns about each user over time.

Architecture:
  - Tier 1 — Working Memory (Redis): current session messages
  - Tier 2 — Episodic Memory (PostgreSQL): user facts, past conversation summaries
  - Tier 3 — Semantic Memory (Pinecone): knowledge-base retrieval via embeddings
  - Claude API for generation with all three memory tiers as context
  - Bilingual support (EN/ES)

Capabilities:
  - Trip planning & itinerary generation
  - Property Q&A & investment guidance
  - Legal/tax guidance (with disclaimers)
  - Restaurant & experience recommendations
  - Safety information
  - Bitcoin usage guidance in ES
  - Remembers user preferences, budget, timeline across sessions
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from uuid import uuid4

from .memory import ConversationMemory, MemoryConfig
from .models import ChatMessage, MemorySnapshot, MessageRole

logger = logging.getLogger(__name__)


@dataclass
class ConciergeConfig:
    """Configuration for the AI Concierge."""

    anthropic_api_key: str
    anthropic_model: str = "claude-sonnet-4-20250514"
    pinecone_api_key: str = ""
    pinecone_index: str = "gateway-es-knowledge"
    max_context_chunks: int = 5
    temperature: float = 0.7

    # Redis
    redis_url: str = "redis://localhost:6379"

    # PostgreSQL (episodic memory)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gateway_es"

    system_prompt: str = """You are the Gateway El Salvador AI Concierge — a knowledgeable, 
friendly, and bilingual (English/Spanish) assistant that helps people discover, explore, 
and invest in El Salvador.

You have deep knowledge of:
- El Salvador's 14 departments and their unique characteristics
- Tourism experiences (beaches, volcanoes, coffee regions, culture, food)
- Real estate market (no MLS, no licensing, current pricing by region)
- Safety transformation (from 104 to 1.9 homicides per 100K)
- Bitcoin as legal tender and how to use it in ES
- Residency and visa pathways
- Cost of living comparisons
- The Gateway El Salvador Foundation and its impact on education

You have a MEMORY of past conversations with each user. Use the provided memory context
to personalize your responses — reference their stated preferences, budget, timeline,
and interests naturally. Don't repeat facts back robotically; weave them in organically.

Always be helpful, accurate, and enthusiastic about El Salvador while being honest 
about challenges. When providing legal or tax guidance, always include disclaimers 
to consult with professionals.

When you don't know something, say so — don't make up information.
"""


class Concierge:
    """
    RAG-powered AI Concierge with 3-tier memory for Gateway El Salvador.

    Usage::

        config = ConciergeConfig(anthropic_api_key="sk-...")
        concierge = Concierge(config)
        await concierge.initialize()

        result = await concierge.chat(
            message="Show me beach properties under $200K",
            user_id="user_abc",
            conversation_id="conv_123",
        )
    """

    def __init__(self, config: ConciergeConfig):
        self.config = config
        self.client = None  # Anthropic AsyncAnthropic client
        self.memory = ConversationMemory(
            MemoryConfig(
                redis_url=config.redis_url,
                database_url=config.database_url,
                pinecone_api_key=config.pinecone_api_key,
                pinecone_index=config.pinecone_index,
                semantic_top_k=config.max_context_chunks,
                anthropic_api_key=config.anthropic_api_key,
                anthropic_model=config.anthropic_model,
            )
        )

    async def initialize(self) -> None:
        """Initialize Anthropic client and 3-tier memory system."""
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=self.config.anthropic_api_key)
            logger.info("Anthropic client initialized (model=%s).", self.config.anthropic_model)
        except Exception as exc:
            logger.warning("Anthropic client unavailable: %s", exc)

        await self.memory.initialize()

    async def chat(
        self,
        message: str,
        user_id: str | None = None,
        conversation_id: str | None = None,
        language: str = "en",
    ) -> dict:
        """
        Process a chat message through the memory-augmented RAG pipeline.

        Flow:
          1. Recall — assemble context from all 3 memory tiers
          2. Build prompt — system + episodic context + semantic context + conversation
          3. Generate — call Claude with the assembled prompt
          4. Remember — persist the turn into working memory
          5. Return — reply + sources + suggested actions
        """
        conversation_id = conversation_id or uuid4().hex
        user_id = user_id or "anonymous"

        # ── Step 1: Recall ──
        snapshot = await self.memory.recall(user_id, conversation_id, message)

        # ── Step 2: Build prompt ──
        system_prompt = self._build_system_prompt(snapshot)
        messages = self._build_messages(snapshot, message)

        # ── Step 3: Generate ──
        if self.client:
            try:
                response = await self.client.messages.create(
                    model=self.config.anthropic_model,
                    max_tokens=2048,
                    temperature=self.config.temperature,
                    system=system_prompt,
                    messages=messages,
                )
                reply = response.content[0].text
            except Exception as exc:
                logger.error("Claude generation failed: %s", exc)
                reply = self._fallback_reply(message, language)
        else:
            reply = self._fallback_reply(message, language)

        # ── Step 4: Remember ──
        user_msg = ChatMessage(role=MessageRole.USER, content=message)
        assistant_msg = ChatMessage(role=MessageRole.ASSISTANT, content=reply)
        await self.memory.remember(conversation_id, user_msg, assistant_msg, user_id)

        # ── Step 5: Return ──
        sources = [
            {"source": c.source, "score": round(c.score, 3)}
            for c in snapshot.knowledge_chunks
        ]
        return {
            "reply": reply,
            "conversation_id": conversation_id,
            "user_id": user_id,
            "sources": sources,
            "memory_facts": len(snapshot.user_facts),
            "suggested_actions": self._get_suggested_actions(message),
        }

    async def end_conversation(self, user_id: str, conversation_id: str) -> None:
        """
        Close a conversation — extract final facts, summarize, archive.

        Call this when the user leaves the chat or after an inactivity timeout.
        """
        await self.memory.close_conversation(user_id, conversation_id)

    async def forget_user(self, user_id: str) -> None:
        """GDPR right-to-erasure: delete all per-user memory."""
        await self.memory.forget_user(user_id)

    # ── Prompt Assembly ──────────────────────────────

    def _build_system_prompt(self, snapshot: MemorySnapshot) -> str:
        """
        Assemble the system prompt with episodic + semantic context.

        Structure:
          [Base system prompt]
          [Episodic context — user facts + past summaries]
          [Semantic context — knowledge-base chunks]
        """
        parts = [self.config.system_prompt.strip()]

        episodic = snapshot.format_episodic_context()
        if episodic:
            parts.append(
                "\n\n--- MEMORY (what you remember about this user) ---\n" + episodic
            )

        semantic = snapshot.format_semantic_context()
        if semantic:
            parts.append(
                "\n\n--- KNOWLEDGE BASE (retrieved context) ---\n" + semantic
            )

        return "\n".join(parts)

    def _build_messages(self, snapshot: MemorySnapshot, current_message: str) -> list[dict]:
        """
        Build the messages array from working memory + the current turn.

        Working memory already contains the recent conversation history.
        We append the new user message at the end.
        """
        messages = [m.to_api_message() for m in snapshot.recent_messages]
        messages.append({"role": "user", "content": current_message})
        return messages

    # ── Helpers ──────────────────────────────────────

    def _fallback_reply(self, message: str, language: str) -> str:
        """Fallback reply when Claude is unavailable."""
        if language == "es":
            return (
                "¡Hola! Soy el asistente de Gateway El Salvador. "
                "Estoy en desarrollo — ¡pronto podré ayudarte a descubrir todo sobre El Salvador!"
            )
        return (
            "Hello! I'm the Gateway El Salvador AI concierge. "
            "I'm still being set up — soon I'll be able to help you discover everything about El Salvador!"
        )

    def _get_suggested_actions(self, message: str) -> list[str]:
        """Generate contextual suggested actions."""
        msg_lower = message.lower()

        # Contextual suggestions based on what the user is discussing
        if any(w in msg_lower for w in ("property", "house", "invest", "buy", "real estate")):
            return [
                "🏠 Compare properties by region",
                "📊 Get an AI valuation",
                "📋 Property buying process",
                "💰 Financing options",
            ]
        if any(w in msg_lower for w in ("beach", "surf", "coast", "ocean")):
            return [
                "🏖️ Top 10 beaches",
                "🏠 Beachfront properties",
                "🏄 Surf spots guide",
                "🌅 Beach town cost of living",
            ]
        if any(w in msg_lower for w in ("bitcoin", "btc", "crypto", "lightning")):
            return [
                "₿ How Bitcoin works in ES",
                "💳 Where to spend BTC",
                "🏦 Bitcoin banking options",
                "📱 Chivo Wallet guide",
            ]
        if any(w in msg_lower for w in ("safe", "security", "danger", "crime")):
            return [
                "🔒 Safety statistics 2024-2026",
                "📍 Safest regions",
                "🏘️ Gated communities",
                "👮 Security infrastructure",
            ]

        # Default suggestions
        return [
            "🏖️ Best beaches in El Salvador",
            "🏠 Property investment guide",
            "🗺️ Plan a trip",
            "₿ Using Bitcoin in ES",
            "🔒 Safety information",
        ]

    async def ingest_document(self, content: str, metadata: dict) -> None:
        """Ingest a document into the knowledge base (semantic memory)."""
        chunk_id = metadata.get("id", uuid4().hex)
        source = metadata.get("source", "unknown")
        await self.memory.semantic.ingest(chunk_id, content, source, metadata)
