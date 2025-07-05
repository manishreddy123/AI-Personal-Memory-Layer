import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.vectorstore import build_vectorstore
from memory.rag_chain import build_qa_chain


class TestMemorySystem(unittest.TestCase):
    """Test the memory system components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_docs = [
            "Machine learning is a subset of artificial intelligence.",
            "Deep learning uses neural networks with multiple layers.",
            "Natural language processing helps computers understand text."
        ]
    
    @patch('memory.vectorstore.FAISS')
    @patch('memory.vectorstore.OpenAIEmbeddings')
    @patch('memory.vectorstore.RecursiveCharacterTextSplitter')
    def test_vectorstore_creation(self, mock_splitter, mock_embeddings, mock_faiss):
        """Test vectorstore creation with proper document splitting"""
        # Mock text splitter
        mock_splitter_instance = MagicMock()
        mock_splitter.return_value = mock_splitter_instance
        mock_documents = [MagicMock() for _ in self.sample_docs]
        mock_splitter_instance.create_documents.return_value = mock_documents
        
        # Mock embeddings
        mock_embeddings_instance = MagicMock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        # Mock FAISS
        mock_vectorstore = MagicMock()
        mock_faiss.from_documents.return_value = mock_vectorstore
        
        result = build_vectorstore(self.sample_docs)
        
        # Verify text splitter was called with correct parameters
        mock_splitter.assert_called_once_with(chunk_size=500, chunk_overlap=50)
        mock_splitter_instance.create_documents.assert_called_once_with(self.sample_docs)
        
        # Verify embeddings were created
        mock_embeddings.assert_called_once()
        
        # Verify FAISS vectorstore was created
        mock_faiss.from_documents.assert_called_once_with(mock_documents, mock_embeddings_instance)
        
        self.assertEqual(result, mock_vectorstore)
    
    @patch('memory.vectorstore.FAISS')
    @patch('memory.vectorstore.OpenAIEmbeddings')
    @patch('memory.vectorstore.RecursiveCharacterTextSplitter')
    def test_vectorstore_empty_docs(self, mock_splitter, mock_embeddings, mock_faiss):
        """Test vectorstore creation with empty documents"""
        mock_splitter_instance = MagicMock()
        mock_splitter.return_value = mock_splitter_instance
        mock_splitter_instance.create_documents.return_value = []
        
        mock_embeddings_instance = MagicMock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        mock_vectorstore = MagicMock()
        mock_faiss.from_documents.return_value = mock_vectorstore
        
        result = build_vectorstore([])
        
        mock_splitter_instance.create_documents.assert_called_once_with([])
        self.assertEqual(result, mock_vectorstore)
    
    @patch('memory.rag_chain.RetrievalQA')
    @patch('memory.rag_chain.OpenAI')
    def test_qa_chain_creation(self, mock_openai, mock_retrieval_qa):
        """Test QA chain creation"""
        # Mock vectorstore and retriever
        mock_vectorstore = MagicMock()
        mock_retriever = MagicMock()
        mock_vectorstore.as_retriever.return_value = mock_retriever
        
        # Mock LLM
        mock_llm = MagicMock()
        mock_openai.return_value = mock_llm
        
        # Mock QA chain
        mock_qa_chain = MagicMock()
        mock_retrieval_qa.from_chain_type.return_value = mock_qa_chain
        
        result = build_qa_chain(mock_vectorstore)
        
        # Verify retriever was created
        mock_vectorstore.as_retriever.assert_called_once()
        
        # Verify LLM was created with correct temperature
        mock_openai.assert_called_once_with(temperature=0)
        
        # Verify QA chain was created
        mock_retrieval_qa.from_chain_type.assert_called_once_with(
            llm=mock_llm, 
            retriever=mock_retriever
        )
        
        self.assertEqual(result, mock_qa_chain)
    
    @patch('memory.rag_chain.RetrievalQA')
    @patch('memory.rag_chain.OpenAI')
    def test_qa_chain_query_simulation(self, mock_openai, mock_retrieval_qa):
        """Test QA chain query simulation"""
        # Setup mocks
        mock_vectorstore = MagicMock()
        mock_retriever = MagicMock()
        mock_vectorstore.as_retriever.return_value = mock_retriever
        
        mock_llm = MagicMock()
        mock_openai.return_value = mock_llm
        
        mock_qa_chain = MagicMock()
        mock_qa_chain.run.return_value = "Machine learning is a subset of AI."
        mock_retrieval_qa.from_chain_type.return_value = mock_qa_chain
        
        # Create QA chain
        qa_chain = build_qa_chain(mock_vectorstore)
        
        # Simulate a query
        test_query = "What is machine learning?"
        result = qa_chain.run(test_query)
        
        # Verify the query was processed
        mock_qa_chain.run.assert_called_once_with(test_query)
        self.assertEqual(result, "Machine learning is a subset of AI.")
    
    def test_integration_vectorstore_and_qa_chain(self):
        """Test integration between vectorstore and QA chain"""
        with patch('memory.vectorstore.FAISS') as mock_faiss, \
             patch('memory.vectorstore.OpenAIEmbeddings') as mock_embeddings, \
             patch('memory.vectorstore.RecursiveCharacterTextSplitter') as mock_splitter, \
             patch('memory.rag_chain.RetrievalQA') as mock_retrieval_qa, \
             patch('memory.rag_chain.OpenAI') as mock_openai:
            
            # Setup vectorstore mocks
            mock_splitter_instance = MagicMock()
            mock_splitter.return_value = mock_splitter_instance
            mock_splitter_instance.create_documents.return_value = [MagicMock()]
            
            mock_embeddings_instance = MagicMock()
            mock_embeddings.return_value = mock_embeddings_instance
            
            mock_vectorstore = MagicMock()
            mock_retriever = MagicMock()
            mock_vectorstore.as_retriever.return_value = mock_retriever
            mock_faiss.from_documents.return_value = mock_vectorstore
            
            # Setup QA chain mocks
            mock_llm = MagicMock()
            mock_openai.return_value = mock_llm
            
            mock_qa_chain = MagicMock()
            mock_retrieval_qa.from_chain_type.return_value = mock_qa_chain
            
            # Test the integration
            vectorstore = build_vectorstore(self.sample_docs)
            qa_chain = build_qa_chain(vectorstore)
            
            # Verify the vectorstore was passed correctly to QA chain
            mock_vectorstore.as_retriever.assert_called_once()
            mock_retrieval_qa.from_chain_type.assert_called_once_with(
                llm=mock_llm,
                retriever=mock_retriever
            )


if __name__ == '__main__':
    unittest.main()
