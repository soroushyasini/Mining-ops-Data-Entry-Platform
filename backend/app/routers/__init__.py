from .drivers import router as drivers_router
from .trucks import router as trucks_router
from .facilities import router as facilities_router
from .shipments import router as shipments_router
from .bunker_loads import router as bunker_loads_router
from .lab_samples import router as lab_samples_router
from .payments import router as payments_router
from .transport_costs import router as transport_costs_router
from .lookup import router as lookup_router
from .seed import router as seed_router

__all__ = [
    "drivers_router",
    "trucks_router",
    "facilities_router",
    "shipments_router",
    "bunker_loads_router",
    "lab_samples_router",
    "payments_router",
    "transport_costs_router",
    "lookup_router",
    "seed_router",
]
