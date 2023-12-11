import os
import requests
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter, TokenTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.document import Document
from langchain.chains import RetrievalQA

from flask import Flask, request, jsonify
app = Flask(__name__)

persistent_directory = './chroma_db'
embeddings_model = HuggingFaceEmbeddings()

try:
    with open("./open-ai-key.txt", "r") as file:
        open_ai_key = file.readline().strip()
    print('open_ai_key fetched!!!')
except FileNotFoundError:
    open_ai_key = ""
    print('open_ai_key not fetched!!!')
    
llm = OpenAI(openai_api_key=open_ai_key)

r_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=50,
    separators=["\n\n", "\n", "(?<=\. )", " "]
)

@app.route('/rag', methods=['POST'])
def rag():
    data = request.json
    query = data['query']
    docs = data['docs']
    
    docs = Document(page_content=docs)
    paras = r_splitter.split_documents([docs])
    
    vectordb = Chroma.from_documents(
        documents = paras,
        embedding=embeddings_model,
        persist_directory=persistent_directory,
    )
    
        
    new_line = '\n'
    template = f"Use the following pieces of context to answer truthfully.{new_line}If the context does not provide the truthful answer, make the answer as truthful as possible.{new_line}Use 15 words maximum. Keep the response as concise as possible.{new_line}{{context}}{new_line}Question: {{question}}{new_line}Response: "
    QA_CHAIN_PROMPT = PromptTemplate(input_variables=["context", "question"],template=template,)


    qa_chain = RetrievalQA.from_chain_type(llm,
                                          retriever=vectordb.as_retriever(),
                                          return_source_documents=True,
                                          chain_type_kwargs={"prompt": QA_CHAIN_PROMPT})


    answer = qa_chain({"query": query})
    result = {'answer':answer["result"].strip()}
    
    # Return the result
    return jsonify(result)


if __name__ == '__main__':
    
    app.run(debug=True, host='0.0.0.0', port=5000)
