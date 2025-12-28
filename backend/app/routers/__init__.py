"""
Routers module - FastAPI route definitions.

This module contains API endpoint definitions. Business logic is delegated
to the builders module following the Repository/Builder pattern.
"""

from backend.app.routers.experiments import router as experiments_router

__all__ = ["experiments_router"]
