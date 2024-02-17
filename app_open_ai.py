import streamlit as st
from config import *
from qdrant_helper import insert_qdrant_docs, \
    get_search_results


st.set_page_config(page_title="Search Engine", page_icon="🔍", layout="wide")

search_upload = st.sidebar.radio("Select the Analysis Type", \
                                 ('Search', 'Upload Docs'))

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

