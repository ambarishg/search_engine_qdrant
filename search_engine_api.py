from fastapi import FastAPI
from qdrant_helper import get_search_results, insert_qdrant_docs
import uvicorn

app = FastAPI()

@app.get("/api/search")
def search(q: str, category: str = ''):
    return get_search_results(q,category) 



