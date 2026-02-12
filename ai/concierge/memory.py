"""
Conversation Memory — 3-Tier Memory System for the AI Concierge
================================================================

Tier 1 — Working Memory  (Redis)
    Current session messages. Fast read/write. TTL = session duration.
    Key pattern: ``concierge:conv:{conversation_id}:messages``

Tier 2 — Episodic Memory  (PostgreSQL via JSONB)
    Extracted user facts/preferences and conversation summaries.
    Persistent across sessions. Queryable by user_id + category.
    Tables: ``user_facts``, ``conversation_summaries``

Tier 3 — Semantic Memory  (Pinecone)
    Knowledge-base chunks retrieved by embedding similarity.
    Shared across all users (platform knowledge, not per-user).

Usage::

    memory = ConversationMemory(config)
    await memory.initialize()

    # On each incoming message:
    snapshot = await memory.recall(user_id, conversation_id, query)
    # → snapshot contains recent msgs + user facts + knowledge chunks

    # After generating a response:
    await memory.remember(conversation_id, user_msg, assistant_msg)

    # When a conversation ends:
    await memory.close_conversation(user_id, conversation_id)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from .models import (
    ChatMessage,
    ConversationSummary,
    FactCategory,
    MemorySnapshot,
    MessageRole,
    RetrievedChunk,
    UserFact,
)

logger = logging.getLogger(__name__)


# ── Configuration ────────────────────────────────────


@dataclass
class MemoryConfig:
    """Configuration for the 3-tier memory system."""

    # Redis (Tier 1)
    redis_url: str = "redis://localhost:6379"
    working_memory_ttl_seconds: int = 3600 * 4   # 4 hours
    max_working_messages: int = 40               # rolling window

    # PostgreSQL (Tier 2) — uses the app's existing async engine
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gateway_es"

    # Pinecone (Tier 3)
    pinecone_api_key: str = ""
    pinecone_index: str = "gateway-es-knowledge"
    semantic_top_k: int = 5

    # Anthropic — used for fact extraction & summarisation
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    # Episodic recall limits
    max_user_facts: int = 20
    max_past_summaries: int = 3


# ── Tier 1 — Working Memory (Redis) ─────────────────


class WorkingMemory:
    """
    Short-term conversation buffer stored in Redis.

    Each conversation is a Redis list of JSON-serialised ``ChatMessage``
    dicts keyed by ``concierge:conv:{conversation_id}:messages``.
    """

    def __init__(self, redis_url: str, ttl: int, max_messages: int):
        self.redis_url = redis_url
        self.ttl = ttl
        self.max_messages = max_messages
        self._redis = None

    async def initialize(self) -> None:
        try:
            from redis.asyncio import from_url
            self._redis = from_url(self.redis_url, decode_responses=True)
            await self._redis.ping()
            logger.info("Working memory (Redis) connected.")
        except Exception as exc:
            logger.warning("Redis unavailable — falling back to in-process dict: %s", exc)
            self._redis = None
            self._fallback: dict[str, list[dict]] = {}

    def _key(self, conversation_id: str) -> str:
        return f"concierge:conv:{conversation_id}:messages"

    async def append(self, conversation_id: str, message: ChatMessage) -> None:
        """Push a message onto the conversation list."""
        payload = json.dumps(message.to_dict())
        if self._redis:
            key = self._key(conversation_id)
            await self._redis.rpush(key, payload)
            await self._redis.ltrim(key, -self.max_messages, -1)
            await self._redis.expire(key, self.ttl)
        else:
            msgs = self._fallback.setdefault(conversation_id, [])
            msgs.append(message.to_dict())
            if len(msgs) > self.max_messages:
                self._fallback[conversation_id] = msgs[-self.max_messages:]

    async def get_history(self, conversation_id: str) -> list[ChatMessage]:
        """Retrieve the full working-memory window for a conversation."""
        if self._redis:
            raw = await self._redis.lrange(self._key(conversation_id), 0, -1)
            return [ChatMessage.from_dict(json.loads(r)) for r in raw]
        return [
            ChatMessage.from_dict(m)
            for m in self._fallback.get(conversation_id, [])
        ]

    async def clear(self, conversation_id: str) -> None:
        """Remove a conversation's working memory (e.g. on session end)."""
        if self._redis:
            await self._redis.delete(self._key(conversation_id))
        else:
            self._fallback.pop(conversation_id, None)


# ── Tier 2 — Episodic Memory (PostgreSQL JSONB) ─────


class EpisodicMemory:
    """
    Long-term per-user memory stored in PostgreSQL.

    Uses two lightweight tables with JSONB payloads so we don't need
    a migration every time the fact schema evolves.

    Tables (created lazily via ``_ensure_tables``):
      - ``concierge_user_facts``
      - ``concierge_conversation_summaries``
    """

    CREATE_FACTS_TABLE = """
    CREATE TABLE IF NOT EXISTS concierge_user_facts (
        fact_id     TEXT PRIMARY KEY,
        user_id     TEXT NOT NULL,
        category    TEXT NOT NULL,
        content     TEXT NOT NULL,
        confidence  REAL NOT NULL DEFAULT 0.9,
        source_conversation_id TEXT,
        created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        is_active   BOOLEAN NOT NULL DEFAULT TRUE,
        metadata    JSONB DEFAULT '{}'::jsonb
    );
    CREATE INDEX IF NOT EXISTS idx_user_facts_user
        ON concierge_user_facts (user_id, is_active);
    """

    CREATE_SUMMARIES_TABLE = """
    CREATE TABLE IF NOT EXISTS concierge_conversation_summaries (
        summary_id       TEXT PRIMARY KEY,
        user_id          TEXT NOT NULL,
        conversation_id  TEXT NOT NULL UNIQUE,
        summary          TEXT NOT NULL,
        topics           JSONB DEFAULT '[]'::jsonb,
        message_count    INTEGER DEFAULT 0,
        created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        metadata         JSONB DEFAULT '{}'::jsonb
    );
    CREATE INDEX IF NOT EXISTS idx_conv_summaries_user
        ON concierge_conversation_summaries (user_id);
    """

    def __init__(self, database_url: str):
        self.database_url = database_url
        self._engine = None

    async def initialize(self) -> None:
        from sqlalchemy.ext.asyncio import create_async_engine
        self._engine = create_async_engine(self.database_url, pool_size=5)
        await self._ensure_tables()
        logger.info("Episodic memory (PostgreSQL) connected.")

    async def _ensure_tables(self) -> None:
        """Create tables if they don't exist."""
        from sqlalchemy import text
        async with self._engine.begin() as conn:
            await conn.execute(text(self.CREATE_FACTS_TABLE))
            await conn.execute(text(self.CREATE_SUMMARIES_TABLE))

    # ── Facts ──

    async def store_facts(self, facts: list[UserFact]) -> None:
        """Upsert extracted facts for a user."""
        from sqlalchemy import text
        upsert_sql = text("""
            INSERT INTO concierge_user_facts
                (fact_id, user_id, category, content, confidence,
                 source_conversation_id, created_at, updated_at, is_active)
            VALUES
                (:fact_id, :user_id, :category, :content, :confidence,
                 :source_conversation_id, :created_at, :updated_at, :is_active)
            ON CONFLICT (fact_id) DO UPDATE SET
                content    = EXCLUDED.content,
                confidence = EXCLUDED.confidence,
                updated_at = EXCLUDED.updated_at,
                is_active  = EXCLUDED.is_active
        """)
        async with self._engine.begin() as conn:
            for fact in facts:
                await conn.execute(upsert_sql, fact.to_dict())

    async def get_facts(self, user_id: str, limit: int = 20) -> list[UserFact]:
        """Retrieve active facts for a user, most-recent first."""
        from sqlalchemy import text
        sql = text("""
            SELECT fact_id, user_id, category, content, confidence,
                   source_conversation_id, created_at, updated_at, is_active
            FROM concierge_user_facts
            WHERE user_id = :user_id AND is_active = TRUE
            ORDER BY updated_at DESC
            LIMIT :limit
        """)
        async with self._engine.connect() as conn:
            rows = await conn.execute(sql, {"user_id": user_id, "limit": limit})
            return [
                UserFact.from_dict(dict(row._mapping))
                for row in rows.fetchall()
            ]

    async def deactivate_fact(self, fact_id: str) -> None:
        """Soft-delete a fact (e.g. user corrects themselves)."""
        from sqlalchemy import text
        sql = text("""
            UPDATE concierge_user_facts
            SET is_active = FALSE, updated_at = NOW()
            WHERE fact_id = :fact_id
        """)
        async with self._engine.begin() as conn:
            await conn.execute(sql, {"fact_id": fact_id})

    # ── Summaries ──

    async def store_summary(self, summary: ConversationSummary) -> None:
        """Store a conversation summary."""
        from sqlalchemy import text
        sql = text("""
            INSERT INTO concierge_conversation_summaries
                (summary_id, user_id, conversation_id, summary, topics,
                 message_count, created_at)
            VALUES
                (:summary_id, :user_id, :conversation_id, :summary,
                 :topics::jsonb, :message_count, :created_at)
            ON CONFLICT (conversation_id) DO UPDATE SET
                summary       = EXCLUDED.summary,
                topics        = EXCLUDED.topics,
                message_count = EXCLUDED.message_count
        """)
        params = summary.to_dict()
        params["topics"] = json.dumps(params["topics"])
        async with self._engine.begin() as conn:
            await conn.execute(sql, params)

    async def get_summaries(
        self, user_id: str, limit: int = 3
    ) -> list[ConversationSummary]:
        """Retrieve recent conversation summaries for a user."""
        from sqlalchemy import text
        sql = text("""
            SELECT summary_id, user_id, conversation_id, summary,
                   topics, message_count, created_at
            FROM concierge_conversation_summaries
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit
        """)
        async with self._engine.connect() as conn:
            rows = await conn.execute(sql, {"user_id": user_id, "limit": limit})
            results = []
            for row in rows.fetchall():
                data = dict(row._mapping)
                # topics comes back as a Python list from JSONB
                if isinstance(data.get("topics"), str):
                    data["topics"] = json.loads(data["topics"])
                results.append(ConversationSummary.from_dict(data))
            return results

    # ── GDPR / Privacy ──

    async def forget_user(self, user_id: str) -> None:
        """Delete all episodic memory for a user (GDPR right-to-erasure)."""
        from sqlalchemy import text
        async with self._engine.begin() as conn:
            await conn.execute(
                text("DELETE FROM concierge_user_facts WHERE user_id = :uid"),
                {"uid": user_id},
            )
            await conn.execute(
                text("DELETE FROM concierge_conversation_summaries WHERE user_id = :uid"),
                {"uid": user_id},
            )
        logger.info("Erased all episodic memory for user %s", user_id)


# ── Tier 3 — Semantic Memory (Pinecone) ─────────────


class SemanticMemory:
    """
    Knowledge-base retrieval via Pinecone vector search.

    This is *shared* memory — not per-user. It holds the platform's
    proprietary content (guides, property data, FAQs, legal info)
    that the concierge retrieves to ground its answers.
    """

    def __init__(self, api_key: str, index_name: str, top_k: int = 5):
        self.api_key = api_key
        self.index_name = index_name
        self.top_k = top_k
        self._index = None
        self._embed_fn = None

    async def initialize(self) -> None:
        if not self.api_key:
            logger.warning("Pinecone API key not set — semantic memory disabled.")
            return
        try:
            from pinecone import Pinecone
            pc = Pinecone(api_key=self.api_key)
            self._index = pc.Index(self.index_name)
            logger.info("Semantic memory (Pinecone/%s) connected.", self.index_name)
        except Exception as exc:
            logger.warning("Pinecone unavailable: %s", exc)

    async def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        """Embed a query and retrieve the most-relevant knowledge chunks."""
        if self._index is None:
            return []

        k = top_k or self.top_k

        try:
            # Use Pinecone's built-in inference for embedding
            embedding = await self._embed(query)

            results = self._index.query(
                vector=embedding,
                top_k=k,
                include_metadata=True,
            )
            return [
                RetrievedChunk(
                    chunk_id=match["id"],
                    content=match.get("metadata", {}).get("text", ""),
                    source=match.get("metadata", {}).get("source", "unknown"),
                    score=match["score"],
                    metadata=match.get("metadata", {}),
                )
                for match in results.get("matches", [])
            ]
        except Exception as exc:
            logger.error("Semantic retrieval failed: %s", exc)
            return []

    async def _embed(self, text: str) -> list[float]:
        """
        Generate an embedding for the given text.

        Uses Anthropic's voyage-3 via Pinecone inference, or falls back
        to a local sentence-transformers model.
        """
        # TODO: Replace with your chosen embedding provider.
        # Option A — Pinecone Inference:
        #   from pinecone import Pinecone
        #   pc = Pinecone(api_key=self.api_key)
        #   embedding = pc.inference.embed("multilingual-e5-large", [text])
        #
        # Option B — OpenAI embeddings:
        #   response = openai.embeddings.create(input=text, model="text-embedding-3-small")
        #   return response.data[0].embedding
        #
        # Option C — Local sentence-transformers (no API cost):
        #   from sentence_transformers import SentenceTransformer
        #   model = SentenceTransformer("all-MiniLM-L6-v2")
        #   return model.encode(text).tolist()
        raise NotImplementedError(
            "Configure an embedding provider in SemanticMemory._embed()"
        )

    async def ingest(self, chunk_id: str, text: str, source: str, metadata: dict | None = None) -> None:
        """Add a document chunk to the knowledge base."""
        if self._index is None:
            return
        embedding = await self._embed(text)
        meta = {"text": text, "source": source, **(metadata or {})}
        self._index.upsert(vectors=[{"id": chunk_id, "values": embedding, "metadata": meta}])


# ── Fact Extraction (LLM pass) ───────────────────────


FACT_EXTRACTION_PROMPT = """\
You are analyzing a conversation between a user and the Gateway El Salvador AI Concierge.
Extract any **new facts, preferences, or intentions** the user has revealed.

Return a JSON array of objects. Each object must have:
- "category": one of {categories}
- "content": the fact in a concise sentence (3rd person, e.g. "User is interested in…")
- "confidence": float 0.0–1.0

Only include facts explicitly stated or strongly implied. Do NOT invent or assume.
If there are no new facts, return an empty array: []

Conversation (last {n} messages):
{conversation}

Existing known facts (do NOT repeat these):
{existing_facts}

Respond with ONLY the JSON array, no markdown fencing.
"""

SUMMARISATION_PROMPT = """\
Summarize the following conversation between a user and the Gateway El Salvador AI Concierge.
Capture the key topics discussed, any decisions made, and what the user is interested in.
Write 2-3 sentences max. Be factual and concise.

Conversation:
{conversation}

Also return a JSON array of short topic tags (e.g. ["beach property", "La Libertad", "investment"]).

Respond in this exact JSON format (no markdown fencing):
{{"summary": "...", "topics": ["...", "..."]}}
"""


class FactExtractor:
    """Uses Claude to extract user facts from conversations."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def extract_facts(
        self,
        messages: list[ChatMessage],
        existing_facts: list[UserFact],
        user_id: str,
        conversation_id: str,
    ) -> list[UserFact]:
        """Run an LLM pass to extract new user facts from recent messages."""
        if not self.api_key or len(messages) < 2:
            return []

        categories = ", ".join(f'"{c.value}"' for c in FactCategory)
        conversation_text = "\n".join(
            f"{m.role.value}: {m.content}" for m in messages[-10:]
        )
        existing_text = "\n".join(
            f"- [{f.category.value}] {f.content}" for f in existing_facts
        ) or "(none)"

        prompt = FACT_EXTRACTION_PROMPT.format(
            categories=categories,
            n=min(len(messages), 10),
            conversation=conversation_text,
            existing_facts=existing_text,
        )

        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=self.api_key)
            response = await client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            parsed = json.loads(raw)

            return [
                UserFact(
                    user_id=user_id,
                    category=FactCategory(item["category"]),
                    content=item["content"],
                    confidence=item.get("confidence", 0.8),
                    source_conversation_id=conversation_id,
                )
                for item in parsed
                if "category" in item and "content" in item
            ]
        except Exception as exc:
            logger.warning("Fact extraction failed: %s", exc)
            return []

    async def summarize_conversation(
        self,
        messages: list[ChatMessage],
        user_id: str,
        conversation_id: str,
    ) -> ConversationSummary | None:
        """Summarize a full conversation into a short paragraph + topic tags."""
        if not self.api_key or len(messages) < 4:
            return None

        conversation_text = "\n".join(
            f"{m.role.value}: {m.content}" for m in messages
        )
        prompt = SUMMARISATION_PROMPT.format(conversation=conversation_text)

        try:
            from anthropic import AsyncAnthropic
            client = AsyncAnthropic(api_key=self.api_key)
            response = await client.messages.create(
                model=self.model,
                max_tokens=512,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text.strip()
            parsed = json.loads(raw)

            return ConversationSummary(
                user_id=user_id,
                conversation_id=conversation_id,
                summary=parsed.get("summary", ""),
                topics=parsed.get("topics", []),
                message_count=len(messages),
            )
        except Exception as exc:
            logger.warning("Conversation summarisation failed: %s", exc)
            return None


# ── Orchestrator ─────────────────────────────────────


class ConversationMemory:
    """
    Unified 3-tier memory system for the AI Concierge.

    Coordinates Working, Episodic, and Semantic memory to produce
    a ``MemorySnapshot`` at inference time.

    Lifecycle:
      1. ``initialize()``   — connect to Redis, PostgreSQL, Pinecone
      2. ``recall()``        — gather context before generating a reply
      3. ``remember()``      — persist the user + assistant messages
      4. ``close_conversation()`` — summarize & archive the conversation
      5. ``forget_user()``   — GDPR erasure
    """

    def __init__(self, config: MemoryConfig):
        self.config = config
        self.working = WorkingMemory(
            redis_url=config.redis_url,
            ttl=config.working_memory_ttl_seconds,
            max_messages=config.max_working_messages,
        )
        self.episodic = EpisodicMemory(database_url=config.database_url)
        self.semantic = SemanticMemory(
            api_key=config.pinecone_api_key,
            index_name=config.pinecone_index,
            top_k=config.semantic_top_k,
        )
        self._extractor = FactExtractor(
            api_key=config.anthropic_api_key,
            model=config.anthropic_model,
        )

    async def initialize(self) -> None:
        """Connect all three memory tiers."""
        await self.working.initialize()
        try:
            await self.episodic.initialize()
        except Exception as exc:
            logger.warning("Episodic memory (PostgreSQL) unavailable: %s", exc)
        try:
            await self.semantic.initialize()
        except Exception as exc:
            logger.warning("Semantic memory (Pinecone) unavailable: %s", exc)
        logger.info("ConversationMemory initialized (3-tier).")

    # ── Core API ──

    async def recall(
        self,
        user_id: str,
        conversation_id: str,
        query: str,
    ) -> MemorySnapshot:
        """
        Assemble the full memory context for the current turn.

        Called *before* generating a response.
        """
        # Tier 1 — recent messages from this conversation
        recent = await self.working.get_history(conversation_id)

        # Tier 2 — user facts + past conversation summaries
        facts = await self._safe(self.episodic.get_facts, user_id, self.config.max_user_facts)
        summaries = await self._safe(
            self.episodic.get_summaries, user_id, self.config.max_past_summaries
        )

        # Tier 3 — knowledge base retrieval
        chunks = await self._safe(self.semantic.retrieve, query)

        return MemorySnapshot(
            recent_messages=recent,
            user_facts=facts or [],
            past_summaries=summaries or [],
            knowledge_chunks=chunks or [],
        )

    async def remember(
        self,
        conversation_id: str,
        user_message: ChatMessage,
        assistant_message: ChatMessage,
        user_id: str | None = None,
    ) -> None:
        """
        Persist a turn (user msg + assistant response) into working memory.
        Triggers background fact extraction every N messages.

        Called *after* generating a response.
        """
        await self.working.append(conversation_id, user_message)
        await self.working.append(conversation_id, assistant_message)

        # Trigger fact extraction periodically (every 4 turns = 8 messages)
        if user_id:
            history = await self.working.get_history(conversation_id)
            if len(history) % 8 == 0 and len(history) >= 8:
                await self._extract_and_store_facts(user_id, conversation_id, history)

    async def close_conversation(self, user_id: str, conversation_id: str) -> None:
        """
        Finalize a conversation: extract remaining facts, summarize, and archive.

        Should be called when the user explicitly ends the chat,
        or after an inactivity timeout.
        """
        history = await self.working.get_history(conversation_id)
        if not history:
            return

        # Final fact extraction
        await self._extract_and_store_facts(user_id, conversation_id, history)

        # Summarize
        summary = await self._extractor.summarize_conversation(
            history, user_id, conversation_id
        )
        if summary:
            await self._safe(self.episodic.store_summary, summary)

        # Clear working memory
        await self.working.clear(conversation_id)
        logger.info(
            "Conversation %s closed — %d messages summarized.", conversation_id, len(history)
        )

    async def forget_user(self, user_id: str) -> None:
        """GDPR right-to-erasure: delete all per-user memory."""
        await self._safe(self.episodic.forget_user, user_id)
        logger.info("All memory erased for user %s", user_id)

    # ── Internal helpers ──

    async def _extract_and_store_facts(
        self, user_id: str, conversation_id: str, history: list[ChatMessage]
    ) -> None:
        """Extract new facts and persist them."""
        existing = await self._safe(self.episodic.get_facts, user_id) or []
        new_facts = await self._extractor.extract_facts(
            history, existing, user_id, conversation_id
        )
        if new_facts:
            await self._safe(self.episodic.store_facts, new_facts)
            logger.info("Extracted %d new facts for user %s", len(new_facts), user_id)

    @staticmethod
    async def _safe(fn, *args, **kwargs):
        """Call an async function, swallowing exceptions so one tier
        failing doesn't break the whole memory pipeline."""
        try:
            return await fn(*args, **kwargs)
        except Exception as exc:
            logger.warning("Memory tier call failed (%s): %s", fn.__qualname__, exc)
            return None
