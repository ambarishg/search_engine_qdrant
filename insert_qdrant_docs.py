from config import *

from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer

import qdrant_client as qc
import qdrant_client.http.models as qmodels
from qdrant_client.http.models import *

import os
import uuid

def get_pdf_data(file_path, num_pages = 1):
    reader = PdfReader(file_path)
    full_doc_text = ""
    pages = reader.pages
    num_pages = len(pages) 
    
    try:
        for page in range(num_pages):
            current_page = reader.pages[page]
            text = current_page.extract_text()
            full_doc_text += text
    except:
        print("Error reading file")
    finally:
        return full_doc_text
    

def get_chunks(fulltext:str,chunk_length =500) -> list:
    text = fulltext

    chunks = []
    while len(text) > chunk_length:
        last_period_index = text[:chunk_length].rfind('.')
        if last_period_index == -1:
            last_period_index = chunk_length
        chunks.append(text[:last_period_index])
        text = text[last_period_index+1:]
    chunks.append(text)

    return chunks

model = SentenceTransformer(MODEL_NAME)
client = qc.QdrantClient(url=URL)
METRIC = qmodels.Distance.COSINE

def insert_qdrant_docs(FILE_PATH,CATEGORY):
    FILES = os.listdir(FILE_PATH)
    FILES_FULL_PATH = [FILE_PATH + file for file in FILES]
    for filename in FILES_FULL_PATH:
        print(f'Processing file: {filename}')
        full_doc_text = get_pdf_data(filename)
        print(f'Full doc text length: {len(full_doc_text)}')
        payloads = []
        li_id = []
        corpus = []
        Lines =get_chunks(full_doc_text,500)
        for token in Lines:
            corpus.append(token)
            payloads.append({"token":token,
                            "filename": os.path.basename(filename),
                            "Category":CATEGORY,
                            "type":"pdf"})
            li_id.append(str(uuid.uuid4()))
        embeddings_all = model.encode(corpus, convert_to_tensor=True)
        print(f'Full embeddings length: {len(embeddings_all)}')

        CHUNK_SIZE = 100
        for i in range(0, len(embeddings_all), CHUNK_SIZE):
            if(i+CHUNK_SIZE > len(embeddings_all) -1):
                new_chunk = len(embeddings_all) -1
            else:
                new_chunk = i+CHUNK_SIZE -1
            print("Inserting chunk", i , "to", new_chunk)
            client.upsert(
                collection_name=COLLECTION_NAME,
                points=qmodels.Batch(
                    ids = li_id[i:new_chunk],
                    vectors=embeddings_all[i:new_chunk].tolist(),
                    payloads=payloads[i:new_chunk]
                ),
            )