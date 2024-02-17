sudo docker run -p 6333:6333 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant

cd search_engine
uvicorn search_engine_api:app --port 8000

streamlit run app_open_ai_fast_api.py