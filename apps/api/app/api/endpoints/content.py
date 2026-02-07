"""
Content & SEO endpoints — blog posts, guides, AI-generated content.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class ContentArticle(BaseModel):
    """A content article or guide."""

    id: str
    slug: str
    title: str
    title_es: str
    excerpt: str
    excerpt_es: str
    category: str  # travel, investment, culture, safety, bitcoin, expat
    language: str
    published_at: str | None
    thumbnail_url: str | None
    read_time_minutes: int


class ContentListResponse(BaseModel):
    """Paginated content listing."""

    articles: list[ContentArticle]
    total: int
    page: int
    page_size: int


@router.get("/", response_model=ContentListResponse)
async def list_content(
    category: str | None = None,
    language: str = "en",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
) -> ContentListResponse:
    """List published content articles and guides."""
    # TODO: Query database with filters
    return ContentListResponse(articles=[], total=0, page=page, page_size=page_size)


@router.get("/{slug}")
async def get_article(slug: str, language: str = "en") -> dict:
    """Get a full content article by slug."""
    # TODO: Fetch from database
    return {"slug": slug, "language": language, "content": "Coming soon"}


@router.post("/generate")
async def generate_content(topic: str, language: str = "en") -> dict:
    """Queue AI content generation for a topic (admin only)."""
    # TODO: Auth check + queue content generation job
    return {"status": "queued", "topic": topic, "language": language}
