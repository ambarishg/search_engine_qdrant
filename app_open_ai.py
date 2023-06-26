import streamlit as st
from PIL import Image
from sentence_transformers import SentenceTransformer
from openai_helper import create_prompt, generate_answer
import pandas as pd
import qdrant_client as qc
import qdrant_client.http.models as qmodels
from qdrant_client.http.models import *
from config import *
from insert_qdrant_docs import insert_qdrant_docs


@st.cache_resource
def get_model_for_documents(MODEL_NAME:str) -> SentenceTransformer:
    model = SentenceTransformer(MODEL_NAME)
    return model

client = qc.QdrantClient(url=URL)
METRIC = qmodels.Distance.COSINE

st.set_page_config(page_title="Search Engine", page_icon="🔍", layout="wide")

search_upload = st.sidebar.radio("Select the Analysis Type", \
                                 ('Search', 'Upload Docs'))

def get_search_results(user_input, CATEGORY):
    model = get_model_for_documents(MODEL_NAME)
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
    search_result = client.search(
                                    collection_name=COLLECTION_NAME,
                                    query_vector=xq.tolist(), 
                                    query_filter=query_filter,
                                    limit=5)
    contexts =""
    for result in search_result:
        contexts +=  result.payload['token']+"\n---\n"

    context= "\n\n".join(contexts)
    conversation=[{"role": "system", "content": "Assistant is a large language model trained by OpenAI."}]
    prompt = create_prompt(context,user_input)            
    conversation.append({"role": "assistant", "content": prompt})
    conversation.append({"role": "user", "content": user_input})
    reply = generate_answer(conversation)
    return reply

if search_upload == 'Search':
    st.header('Search Engine - Document')

    st.markdown(" Input the Text and click Submit"       )
    user_input = st.text_input('Enter your question here:')
    CATEGORY = st.text_input('Enter the category here:')

    if st.button('Submit'):
        reply = get_search_results(user_input, CATEGORY)
        st.write(reply)

if search_upload == 'Upload Docs':

    upload_category = st.selectbox('Select the Upload Type', ['Local File Path','S3'])
    if upload_category == 'S3':
        s3_bucket_name = st.text_input('Enter the S3 bucket here:')
        CATEGORY = st.text_input('Enter the category here:')
        if st.button('Submit'):
            pass
    else:
        file_path = st.text_input('Enter the file path here:')
        CATEGORY = st.text_input('Enter the category here:')
        if st.button('Submit'):
            insert_qdrant_docs(file_path,CATEGORY)

