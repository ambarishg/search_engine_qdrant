import streamlit as st
from config import *
from qdrant_helper import insert_qdrant_docs, \
    get_search_results
import requests

URL = "http://localhost:8000/"

st.set_page_config(page_title="Search Engine", page_icon="🔍")

st.header('Search Engine - Document')

st.markdown(" Input the Text and click Submit"       )
user_input = st.text_input('Enter your question here:')
CATEGORY = st.text_input('Enter the category here:')

if st.button('Submit'):
    # defining a params dict for the parameters to be sent to the API
    if CATEGORY == '':
        PARAMS = {'q':user_input}
    else:
        PARAMS = {'q':user_input, 'category':CATEGORY}
    r = requests.get(URL + "api/search",params= PARAMS)
    reply = r.json()
    st.write(reply)

