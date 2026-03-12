from fastapi import APIRouter

from .auth import get_auth_router
from .storage import get_storage_router
from .billing import get_billing_router
from .observability import get_observability_router

def auth_routes() -> APIRouter:
    """
    Returns the authentication router.
    """
    return get_auth_router()

def storage_routes() -> APIRouter:
    """
    Returns the storage router.
    """
    return get_storage_router()

def billing_routes() -> APIRouter:
    """
    Returns the billing router.
    """
    return get_billing_router()

def observability_routes() -> APIRouter:
    """
    Returns the observability router.
    """
    return get_observability_router()