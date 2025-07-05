import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_api_keys
from memory.vectorstore import build_vectorstore
from memory.rag_chain import build_qa_chain
from agent.memory_agent import build_agent


class TestMainFlow(unittest.TestCase):
    """Test the main application flow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_docs = [
            "This is a test document about machine learning.",
            "Another document about artificial intelligence.",
            "A third document about data science."
        ]
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_key',
        'NOTION_API_KEY': 'test_notion_key',
        'NOTION_DB_ID': 'test_db_id',
        'GOOGLE_CLIENT_SECRET_FILE': 'test_credentials.json'
    })
    def test_load_api_keys(self):
        """Test API key loading"""
        load_api_keys()
        self.assertEqual(os.environ.get('OPENAI_API_KEY'), 'test_key')
        self.assertEqual(os.environ.get('NOTION_API_KEY'), 'test_notion_key')
    
    @patch('memory.vectorstore.OpenAIEmbeddings')
    @patch('memory.vectorstore.FAISS')
    def test_build_vectorstore(self, mock_faiss, mock_embeddings):
        """Test vectorstore creation"""
        mock_vectorstore = MagicMock()
        mock_faiss.from_documents.return_value = mock_vectorstore
        
        result = build_vectorstore(self.sample_docs)
        
        self.assertIsNotNone(result)
        mock_faiss.from_documents.assert_called_once()
        mock_embeddings.assert_called_once()
    
    @patch('memory.rag_chain.OpenAI')
    @patch('memory.rag_chain.RetrievalQA')
    def test_build_qa_chain(self, mock_retrieval_qa, mock_openai):
        """Test QA chain creation"""
        mock_vectorstore = MagicMock()
        mock_retriever = MagicMock()
        mock_vectorstore.as_retriever.return_value = mock_retriever
        mock_qa_chain = MagicMock()
        mock_retrieval_qa.from_chain_type.return_value = mock_qa_chain
        
        result = build_qa_chain(mock_vectorstore)
        
        self.assertIsNotNone(result)
        mock_vectorstore.as_retriever.assert_called_once()
        mock_retrieval_qa.from_chain_type.assert_called_once()
    
    @patch('agent.memory_agent.OpenAI')
    @patch('agent.memory_agent.initialize_agent')
    def test_build_agent(self, mock_initialize_agent, mock_openai):
        """Test agent creation"""
        mock_qa_chain = MagicMock()
        mock_agent = MagicMock()
        mock_initialize_agent.return_value = mock_agent
        
        result = build_agent(mock_qa_chain)
        
        self.assertIsNotNone(result)
        mock_initialize_agent.assert_called_once()
        mock_openai.assert_called_once()


if __name__ == '__main__':
    unittest.main()
