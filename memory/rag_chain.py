from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama

def build_qa_chain(vectorstore):
    retriever = vectorstore.as_retriever()
    llm = Ollama(model="llama3.2", temperature=0)
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return qa
