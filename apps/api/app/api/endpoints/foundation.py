"""
Foundation Impact endpoints — transparency dashboard data.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ImpactMetrics(BaseModel):
    """Aggregate impact metrics for the Foundation dashboard."""

    total_revenue_generated_usd: float
    foundation_allocation_usd: float
    allocation_percentage: float
    students_tutored: int
    meals_served: int
    devices_deployed: int
    schools_in_network: int
    solar_installations: int
    supply_kits_distributed: int


class SchoolProfile(BaseModel):
    """A school in the Foundation network."""

    id: str
    name: str
    department: str
    municipio: str
    canton: str
    student_count: int
    has_devices: bool
    has_solar: bool
    has_connectivity: bool
    latitude: float
    longitude: float


@router.get("/impact", response_model=ImpactMetrics)
async def get_impact_metrics() -> ImpactMetrics:
    """Get current Foundation impact metrics."""
    # TODO: Aggregate from database + blockchain verification
    return ImpactMetrics(
        total_revenue_generated_usd=0,
        foundation_allocation_usd=0,
        allocation_percentage=10.0,
        students_tutored=0,
        meals_served=0,
        devices_deployed=0,
        schools_in_network=0,
        solar_installations=0,
        supply_kits_distributed=0,
    )


@router.get("/schools", response_model=list[SchoolProfile])
async def list_schools() -> list[SchoolProfile]:
    """List all schools in the Foundation network."""
    # TODO: Query database
    return []


@router.get("/transactions")
async def get_impact_transactions(limit: int = 50) -> dict:
    """Get blockchain-verified fund allocation transactions."""
    # TODO: Query Stellar/Polygon for on-chain transactions
    return {"transactions": [], "total": 0}
