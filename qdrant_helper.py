from config import *

import qdrant_client as qc
import qdrant_client.http.models as qmodels
from qdrant_client.http.models import *
import os
import uuid

from azure_openai_helper import generate_answer_from_context
from pdf_helper import get_pdf_data, get_chunks
from model_helper import *

def get_qdrant_client():
    client = qc.QdrantClient(url=URL)
    METRIC = qmodels.Distance.COSINE
    return client


client = get_qdrant_client()

#   Inserting documents into Qdrant
#   FILE_PATH: path to the folder containing the pdf files
#   CATEGORY: category of the documents
def insert_qdrant_docs(FILE_PATH,CATEGORY) -> None:
    model = load_model()
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

#   Searching documents in Qdrant
#   user_input: user query
#   CATEGORY: category of the documents

def get_search_results(user_input, CATEGORY) -> str:
    contexts = retrieve_context(user_input, CATEGORY)
    reply = generate_answer_from_context(user_input, contexts)
    return reply

def retrieve_context(user_input, CATEGORY):
    model = load_model()
    xq = model.encode(user_input,convert_to_tensor=True)
    if CATEGORY == '':
        query_filter = None
    else:
        query_filter=qmodels.Filter(
            must= [
                FieldCondition(
                    key="Category",
                    match=models.MatchValue(value=CATEGORY),
                )
            ],
        )
    search_result = client.search(collection_name=COLLECTION_NAME,
                                    query_vector=xq.tolist(), 
                                    query_filter=query_filter,
                                    limit=5)
    contexts =""
    for result in search_result:
        contexts +=  result.payload['token']+"\n---\n"
    return contexts

def retrieve_context_semantic_ranker(user_input, 
                                     CATEGORY,
                                     RANKER_RESULTS_LIMIT = 5,
                                     RESULTS_LIMIT = 25,
                                    ) -> str:
    model = load_model()
    xq = model.encode(user_input,convert_to_tensor=True)
    if CATEGORY == '':
        query_filter = None
    else:
        query_filter=qmodels.Filter(
            must= [
                FieldCondition(
                    key="Category",
                    match=models.MatchValue(value=CATEGORY),
                )
            ],
        )
    search_result = client.search(collection_name=COLLECTION_NAME,
                                    query_vector=xq.tolist(), 
                                    query_filter=query_filter,
                                    limit=RESULTS_LIMIT)
    
    contexts_list = []
    for result in search_result:
        contexts_list.append(result.payload['token'])

    cross_encoder = CrossEncoder(CROSSENCODER_MODEL_NAME)
    cross_inp = [[user_input, hit] for hit in contexts_list]
    cross_scores = cross_encoder.predict(cross_inp)

    cross_scores_text = []
    cross_scores_length = len(cross_scores)
    for i in range(cross_scores_length):
        d = {}
        d['score'] = cross_scores[i]
        d['text'] = contexts_list[i]
        cross_scores_text.append(d)
    
    hits = sorted(cross_scores_text, key=lambda x: x['score'], reverse=True)
    contexts =""
    hits_selected = hits[:RANKER_RESULTS_LIMIT]
    contexts =""
    for i in range(len(hits_selected)):
        contexts  +=  hits_selected[i]['text']+"\n---\n"
    
    return contexts 


