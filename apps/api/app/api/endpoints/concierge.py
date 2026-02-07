"""
AI Concierge endpoints — bilingual RAG-powered chatbot.
"""

from fastapi import APIRouter, WebSocket
from pydantic import BaseModel

router = APIRouter()


class ChatMessage(BaseModel):
    """A single chat message."""

    role: str  # "user" or "assistant"
    content: str
    language: str = "en"  # "en" or "es"


class ChatRequest(BaseModel):
    """Chat request with conversation history."""

    message: str
    language: str = "en"
    conversation_id: str | None = None
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    """Chat response from the AI concierge."""

    reply: str
    conversation_id: str
    sources: list[str] = []
    suggested_actions: list[str] = []


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Send a message to the AI concierge."""
    # TODO: RAG pipeline — retrieve from vector DB, generate with Claude
    return ChatResponse(
        reply="¡Hola! I'm the Gateway El Salvador AI concierge. I'm still being set up — check back soon!",
        conversation_id=request.conversation_id or "new-conversation",
        sources=[],
        suggested_actions=["Explore beaches", "View properties", "Plan a trip"],
    )


@router.websocket("/ws")
async def concierge_websocket(websocket: WebSocket) -> None:
    """Real-time WebSocket connection for the AI concierge."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # TODO: Process through RAG pipeline
            await websocket.send_text(
                '{"reply": "WebSocket concierge coming soon!", "sources": []}'
            )
    except Exception:
        await websocket.close()
