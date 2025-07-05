from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

def build_vectorstore(data):
    """Build vectorstore with free HuggingFace embeddings"""
    documents = [Document(page_content=item) for item in data]
    
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        vectorstore = FAISS.from_documents(documents, embeddings)
        print(f"Successfully created vectorstore with {len(documents)} documents")
        return vectorstore
        
    except Exception as e:
        print(f"ERROR: Unexpected error creating vectorstore: {e}")
        print("Creating fallback vectorstore...")
        
        if documents:
            from langchain_community.embeddings import FakeEmbeddings
            fake_embeddings = FakeEmbeddings(size=384)  # Match MiniLM dimension
            vectorstore = FAISS.from_documents(documents, fake_embeddings)
            return vectorstore
        else:
            return None
