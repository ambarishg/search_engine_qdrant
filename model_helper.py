from sentence_transformers import SentenceTransformer,CrossEncoder
from config import MODEL_NAME

def load_model():
    return SentenceTransformer(MODEL_NAME)