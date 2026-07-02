from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Optional
import os

from db_connector import LocalSQLiteConnector
from embedder import generate_embedding, compute_cosine_similarity

app = FastAPI(title="Fiscus — Regulatory Intelligence API")

db = LocalSQLiteConnector()

# Mount frontend static files
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if not os.path.exists(frontend_dir):
    os.makedirs(frontend_dir)

app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/api/updates")
async def get_updates(limit: int = 50):
    updates = db.get_updates(limit=limit)
    # Remove binary embedding before returning JSON
    for u in updates:
        u.pop("embedding", None)
    return updates

@app.get("/api/search")
async def search_updates(q: str = Query(..., min_length=2)):
    # 1. Generate embedding for query
    query_vector = await generate_embedding(q)
    if not query_vector:
        return {"error": "Failed to generate embedding for query"}
        
    # 2. Get all updates
    # For a prototype, we pull all and sort in memory. For prod, use a vector DB.
    updates = db.get_updates(limit=1000)
    
    scored_updates = []
    for u in updates:
        vec_bytes = u.get("embedding")
        if vec_bytes:
            score = compute_cosine_similarity(query_vector, vec_bytes)
            u["score"] = score
            scored_updates.append(u)
            
    # Remove binary embedding
    for u in scored_updates:
        u.pop("embedding", None)
        
    # Sort by score descending
    scored_updates.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top 10
    return scored_updates[:10]
