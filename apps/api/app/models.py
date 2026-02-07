"""
SQLAlchemy database models for Gateway El Salvador.
Uses PostgreSQL + PostGIS for geospatial capabilities.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship
from geoalchemy2 import Geometry


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


# ── Property Models ──────────────────────────────────


class Property(Base):
    """A real estate property listing."""

    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False)
    title_es = Column(String(255), nullable=False)
    description = Column(Text)
    description_es = Column(Text)
    property_type = Column(String(50), nullable=False)  # house, apartment, land, commercial
    department = Column(String(100), nullable=False)
    municipio = Column(String(100), nullable=False)
    canton = Column(String(100))
    address = Column(Text)

    # Pricing
    price_usd = Column(Float)
    ai_valuation_usd = Column(Float)
    ai_valuation_confidence = Column(Float)
    rental_yield_estimate = Column(Float)
    appreciation_5yr_estimate = Column(Float)

    # Features
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    area_m2 = Column(Float)
    lot_size_m2 = Column(Float)
    year_built = Column(Integer)
    features = Column(JSONB, default=list)

    # Geospatial
    location = Column(Geometry("POINT", srid=4326))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    # Media
    images = Column(JSONB, default=list)
    virtual_tour_url = Column(String(500))

    # Metadata
    source = Column(String(100))  # scraped, partner, direct
    listing_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    neighborhood_score = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    valuations = relationship("PropertyValuation", back_populates="property")


class PropertyValuation(Base):
    """Historical AI valuations for a property."""

    __tablename__ = "property_valuations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"), nullable=False)
    valuation_usd = Column(Float, nullable=False)
    confidence = Column(Float)
    model_version = Column(String(50))
    features_used = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    property = relationship("Property", back_populates="valuations")


# ── Tour & Experience Models ─────────────────────────


class Tour(Base):
    """A bookable tour or experience."""

    __tablename__ = "tours"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(255), nullable=False)
    title_es = Column(String(255), nullable=False)
    description = Column(Text)
    description_es = Column(Text)
    category = Column(String(50), nullable=False)  # surf, volcano, coffee, culture, food, adventure
    department = Column(String(100), nullable=False)
    price_usd = Column(Float, nullable=False)
    duration_hours = Column(Float)
    max_participants = Column(Integer)
    rating = Column(Float)
    review_count = Column(Integer, default=0)

    # Operator
    operator_name = Column(String(255))
    operator_contact = Column(String(255))

    # Geospatial
    meeting_point = Column(Geometry("POINT", srid=4326))
    latitude = Column(Float)
    longitude = Column(Float)

    # Media
    images = Column(JSONB, default=list)
    thumbnail_url = Column(String(500))

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Content Models ───────────────────────────────────


class Article(Base):
    """A content article, guide, or blog post."""

    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug = Column(String(255), unique=True, nullable=False)
    title = Column(String(255), nullable=False)
    title_es = Column(String(255))
    excerpt = Column(Text)
    excerpt_es = Column(Text)
    body = Column(Text, nullable=False)
    body_es = Column(Text)
    category = Column(String(50))  # travel, investment, culture, safety, bitcoin, expat
    tags = Column(JSONB, default=list)
    seo_keywords = Column(JSONB, default=list)

    # AI generation
    is_ai_generated = Column(Boolean, default=False)
    ai_model_used = Column(String(100))
    human_reviewed = Column(Boolean, default=False)

    # Media
    thumbnail_url = Column(String(500))
    images = Column(JSONB, default=list)

    # Stats
    read_time_minutes = Column(Integer)
    view_count = Column(Integer, default=0)

    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ── Foundation Models ────────────────────────────────


class School(Base):
    """A school in the Foundation network."""

    __tablename__ = "schools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    department = Column(String(100), nullable=False)
    municipio = Column(String(100), nullable=False)
    canton = Column(String(100))
    student_count = Column(Integer)
    teacher_count = Column(Integer)

    # Infrastructure
    has_electricity = Column(Boolean, default=False)
    has_internet = Column(Boolean, default=False)
    has_devices = Column(Boolean, default=False)
    has_solar = Column(Boolean, default=False)
    device_count = Column(Integer, default=0)

    # Geospatial
    location = Column(Geometry("POINT", srid=4326))
    latitude = Column(Float)
    longitude = Column(Float)

    # Metadata
    partner_since = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ImpactTransaction(Base):
    """A Foundation fund allocation record (mirrored on-chain)."""

    __tablename__ = "impact_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    source_transaction_id = Column(String(255))  # Platform booking/payment ID
    amount_usd = Column(Float, nullable=False)
    program = Column(String(100), nullable=False)  # tutoring, nutrition, devices, energy, supplies
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"))
    blockchain_tx_hash = Column(String(255))
    blockchain_network = Column(String(50))  # stellar, polygon
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
