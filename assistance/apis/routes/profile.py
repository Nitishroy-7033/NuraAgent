from fastapi import APIRouter
from core.knowledge.mongo_store import mongo_store

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("")
async def get_profile():
    return await mongo_store.get_profile()

@router.patch("")
async def update_profile(updates: dict):
    await mongo_store.update_profile(updates)
    return {"status": "updated"}
