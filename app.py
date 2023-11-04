# https://chatpdflanchainopenai-phamtung.streamlit.app/

import streamlit as st
from dotenv import load_dotenv
import pickle
from PyPDF2 import PdfReader
from streamlit_extras.add_vertical_space import add_vertical_space
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import os

# Sidebar contents
with st.sidebar:
  st.title('🤗 Hé Lô Phạm Tùng')
  st.markdown('''
  ## About
  This app is an LLM-powered chatbot built using:
  - [Streamlit](https://streamlit.io/)
  - [LangChain](https://python.langchain.com/)
  - [OpenAI](https://platform.openai.com/docs/models) LLM model

  ''')
  add_vertical_space(5)
  st.write('Made with ❤️ by [Prompt Engineer](https://youtube.com/@engineerprompt)')

# load_dotenv()
def main():
  os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']
  st.header("Chat with PDF 💬")
  
  # upload a PDF file
  pdf = st.file_uploader("Upload your PDF", type='pdf')
  # st.write(pdf.name)
  
  if pdf is not None:
    pdf_reader = PdfReader(pdf)
    
    text = ""
    for page in pdf_reader.pages:
      text += page.extract_text()
    # st.write(text)
    
    text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=1000,
      chunk_overlap=200,
      length_function=len
      )
    chunks = text_splitter.split_text(text=text)
    # st.write(chunks)
    
    # embeddings = OpenAIEmbeddings()
    # VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
    
    # # embeddings
    store_name = pdf.name[:-4]
    # st.write(f'{store_name}')
    # st.write(chunks)

    if os.path.exists(f"{store_name}.pkl"):
        with open(f"{store_name}.pkl", "rb") as f:
            VectorStore = pickle.load(f)
        # st.write('Embeddings Loaded from the Disk')
    else:
        embeddings = OpenAIEmbeddings()
        VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
        with open(f"{store_name}.pkl", "wb") as f:
            pickle.dump(VectorStore, f)
    # Accept user questions/query
    # prompt = st.text_input("Ask questions about your PDF file:")
    
    prompt = st.chat_input("Say something")
    if prompt:
      st.write(f"User: {prompt}")
    
    # st.write(prompt)
    if prompt:
      docs = VectorStore.similarity_search(query=prompt, k=3)
      # st.write(docs)
      llm = OpenAI()
      chain = load_qa_chain(llm=llm, chain_type="stuff")
      with get_openai_callback() as cb:
        response = chain.run(input_documents=docs, question=prompt)
        print(cb)
      st.write(f"Bot: {response}")
    
if __name__ == '__main__':
  main()   
