"""Initial schema — departments, municipios, properties, coverage gaps

Revision ID: 0001
Revises: None
Create Date: 2026-02-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # ── Departments ──
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("name_es", sa.String(100), unique=True, nullable=False),
        sa.Column("capital", sa.String(100)),
        sa.Column("area_km2", sa.Float()),
        sa.Column("population", sa.Integer()),
        sa.Column("population_year", sa.Integer()),
        sa.Column("iso_code", sa.String(10)),
        sa.Column("boundary", geoalchemy2.Geometry("MULTIPOLYGON", srid=4326), nullable=True),
        sa.Column("centroid_lat", sa.Float()),
        sa.Column("centroid_lng", sa.Float()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # ── Municipios ──
    op.create_table(
        "municipios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("name_es", sa.String(100), nullable=False),
        sa.Column("department_id", sa.Integer(), sa.ForeignKey("departments.id"), nullable=False),
        sa.Column("population", sa.Integer()),
        sa.Column("population_year", sa.Integer()),
        sa.Column("area_km2", sa.Float()),
        sa.Column("elevation_m", sa.Integer()),
        sa.Column("centroid_lat", sa.Float()),
        sa.Column("centroid_lng", sa.Float()),
        sa.Column("boundary", geoalchemy2.Geometry("MULTIPOLYGON", srid=4326), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("name", "department_id", name="uq_municipio_dept"),
    )

    # ── Properties ──
    op.create_table(
        "properties",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("title_es", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("description_es", sa.Text()),
        sa.Column("property_type", sa.String(50), nullable=False),
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("municipio", sa.String(100), nullable=False),
        sa.Column("municipio_id", sa.Integer(), sa.ForeignKey("municipios.id"), nullable=True),
        sa.Column("canton", sa.String(100)),
        sa.Column("address", sa.Text()),
        sa.Column("price_usd", sa.Float()),
        sa.Column("ai_valuation_usd", sa.Float()),
        sa.Column("ai_valuation_confidence", sa.Float()),
        sa.Column("rental_yield_estimate", sa.Float()),
        sa.Column("appreciation_5yr_estimate", sa.Float()),
        sa.Column("bedrooms", sa.Integer()),
        sa.Column("bathrooms", sa.Integer()),
        sa.Column("area_m2", sa.Float()),
        sa.Column("lot_size_m2", sa.Float()),
        sa.Column("year_built", sa.Integer()),
        sa.Column("features", postgresql.JSONB(), server_default="[]"),
        sa.Column("location", geoalchemy2.Geometry("POINT", srid=4326), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("images", postgresql.JSONB(), server_default="[]"),
        sa.Column("virtual_tour_url", sa.String(500)),
        sa.Column("source", sa.String(100)),
        sa.Column("listing_url", sa.String(500)),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("is_featured", sa.Boolean(), server_default="false"),
        sa.Column("neighborhood_score", sa.Float()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_properties_dept", "properties", ["department"])
    op.create_index("ix_properties_municipio", "properties", ["municipio"])
    op.create_index("ix_properties_type", "properties", ["property_type"])
    op.create_index("ix_properties_price", "properties", ["price_usd"])

    # ── Property Valuations ──
    op.create_table(
        "property_valuations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("property_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("valuation_usd", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float()),
        sa.Column("model_version", sa.String(50)),
        sa.Column("features_used", postgresql.JSONB()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # ── Data Coverage Gaps ──
    op.create_table(
        "data_coverage_gaps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("municipio_id", sa.Integer(), sa.ForeignKey("municipios.id"), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("coverage_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("total_listings", sa.Integer(), server_default="0"),
        sa.Column("listings_with_price", sa.Integer(), server_default="0"),
        sa.Column("listings_with_images", sa.Integer(), server_default="0"),
        sa.Column("listings_with_coordinates", sa.Integer(), server_default="0"),
        sa.Column("avg_images_per_listing", sa.Float(), server_default="0.0"),
        sa.Column("priority", sa.String(20), server_default="'medium'"),
        sa.Column("needs_field_research", sa.Boolean(), server_default="false"),
        sa.Column("field_research_status", sa.String(50), server_default="'not_started'"),
        sa.Column("field_research_notes", sa.Text()),
        sa.Column("field_researcher", sa.String(100)),
        sa.Column("field_research_date", sa.DateTime()),
        sa.Column("last_analyzed", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint("municipio_id", "category", name="uq_gap_municipio_cat"),
    )
    op.create_index("ix_gap_priority", "data_coverage_gaps", ["priority"])
    op.create_index("ix_gap_score", "data_coverage_gaps", ["coverage_score"])

    # ── Tours ──
    op.create_table(
        "tours",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("title_es", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("description_es", sa.Text()),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("price_usd", sa.Float(), nullable=False),
        sa.Column("duration_hours", sa.Float()),
        sa.Column("max_participants", sa.Integer()),
        sa.Column("rating", sa.Float()),
        sa.Column("review_count", sa.Integer(), server_default="0"),
        sa.Column("operator_name", sa.String(255)),
        sa.Column("operator_contact", sa.String(255)),
        sa.Column("meeting_point", geoalchemy2.Geometry("POINT", srid=4326), nullable=True),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("images", postgresql.JSONB(), server_default="[]"),
        sa.Column("thumbnail_url", sa.String(500)),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # ── Articles ──
    op.create_table(
        "articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(255), unique=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("title_es", sa.String(255)),
        sa.Column("excerpt", sa.Text()),
        sa.Column("excerpt_es", sa.Text()),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("body_es", sa.Text()),
        sa.Column("category", sa.String(50)),
        sa.Column("tags", postgresql.JSONB(), server_default="[]"),
        sa.Column("seo_keywords", postgresql.JSONB(), server_default="[]"),
        sa.Column("is_ai_generated", sa.Boolean(), server_default="false"),
        sa.Column("ai_model_used", sa.String(100)),
        sa.Column("human_reviewed", sa.Boolean(), server_default="false"),
        sa.Column("thumbnail_url", sa.String(500)),
        sa.Column("images", postgresql.JSONB(), server_default="[]"),
        sa.Column("read_time_minutes", sa.Integer()),
        sa.Column("view_count", sa.Integer(), server_default="0"),
        sa.Column("is_published", sa.Boolean(), server_default="false"),
        sa.Column("published_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # ── Schools (Foundation) ──
    op.create_table(
        "schools",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("department", sa.String(100), nullable=False),
        sa.Column("municipio", sa.String(100), nullable=False),
        sa.Column("canton", sa.String(100)),
        sa.Column("student_count", sa.Integer()),
        sa.Column("teacher_count", sa.Integer()),
        sa.Column("has_electricity", sa.Boolean(), server_default="false"),
        sa.Column("has_internet", sa.Boolean(), server_default="false"),
        sa.Column("has_devices", sa.Boolean(), server_default="false"),
        sa.Column("has_solar", sa.Boolean(), server_default="false"),
        sa.Column("device_count", sa.Integer(), server_default="0"),
        sa.Column("location", geoalchemy2.Geometry("POINT", srid=4326), nullable=True),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("partner_since", sa.DateTime()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # ── Impact Transactions (Foundation) ──
    op.create_table(
        "impact_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_transaction_id", sa.String(255)),
        sa.Column("amount_usd", sa.Float(), nullable=False),
        sa.Column("program", sa.String(100), nullable=False),
        sa.Column("school_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("schools.id")),
        sa.Column("blockchain_tx_hash", sa.String(255)),
        sa.Column("blockchain_network", sa.String(50)),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("impact_transactions")
    op.drop_table("schools")
    op.drop_table("articles")
    op.drop_table("tours")
    op.drop_table("data_coverage_gaps")
    op.drop_table("property_valuations")
    op.drop_table("properties")
    op.drop_table("municipios")
    op.drop_table("departments")
    op.execute("DROP EXTENSION IF EXISTS postgis;")
