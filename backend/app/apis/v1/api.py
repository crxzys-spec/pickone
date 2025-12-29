from fastapi import APIRouter

from app.apis.v1.endpoints import (
    auth,
    categories,
    draws,
    experts,
    organizations,
    permissions,
    regions,
    roles,
    rules,
    titles,
    uploads,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(
    organizations.router, prefix="/organizations", tags=["organizations"]
)
api_router.include_router(regions.router, prefix="/regions", tags=["regions"])
api_router.include_router(experts.router, prefix="/experts", tags=["experts"])
api_router.include_router(rules.router, prefix="/rules", tags=["rules"])
api_router.include_router(draws.router, prefix="/draws", tags=["draws"])
api_router.include_router(titles.router, prefix="/titles", tags=["titles"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
