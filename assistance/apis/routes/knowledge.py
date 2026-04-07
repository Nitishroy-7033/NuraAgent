from fastapi import APIRouter
from core.knowledge.knowledge_service import knowledge_service
from core.knowledge.mongo_store import mongo_store
from models.request.knowledge_search_request import KnowledgeSearchRequest
from models.request.knowledge_store_request import KnowledgeStoreRequest

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

@router.post("/store")
async def store_knowledge(req: KnowledgeStoreRequest):
    chroma_id = await knowledge_service.store_explicit(
        content=req.content,
        category=req.category,
        tags=req.tags,
    )
    return {"status": "stored", "id": chroma_id}

@router.post("/search")
async def search_knowledge(req: KnowledgeSearchRequest):
    from core.knowledge.chroma_store import chroma_store
    results = await chroma_store.search_knowledge(req.query, n_results=req.n_results)
    return {"results": results, "count": len(results)}

@router.get("/all")
async def get_all_knowledge(limit: int = 50):
    items = await mongo_store.get_all_knowledge(limit=limit)
    return {"items": items, "count": len(items)}

@router.get("/category/{category}")
async def get_by_category(category: str, limit: int = 20):
    items = await mongo_store.get_knowledge_by_category(category=category, limit=limit)
    return {"items": items, "count": len(items)}
