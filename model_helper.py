from sentence_transformers import SentenceTransformer
from config import MODEL_NAME

def load_model():
    return SentenceTransformer(MODEL_NAME)