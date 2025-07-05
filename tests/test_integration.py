import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import json

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestIntegration(unittest.TestCase):
    """Integration tests for the entire application flow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_env_vars = {
            'OPENAI_API_KEY': 'test_openai_key',
            'NOTION_API_KEY': 'test_notion_key',
            'NOTION_DB_ID': 'test_db_id',
            'GOOGLE_CLIENT_SECRET_FILE': 'test_credentials.json'
        }
    
    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_openai_key',
        'NOTION_API_KEY': 'test_notion_key',
        'NOTION_DB_ID': 'test_db_id',
        'GOOGLE_CLIENT_SECRET_FILE': 'test_credentials.json'
    })
    @patch('main.run_chat')
    @patch('main.build_agent')
    @patch('main.build_qa_chain')
    @patch('main.build_vectorstore')
    @patch('main.load_calendar_events')
    @patch('main.load_notion_pages')
    @patch('main.load_gmail_emails')
    @patch('main.load_api_keys')
    def test_full_application_flow(self, mock_load_api_keys, mock_gmail, mock_notion, 
                                 mock_calendar, mock_vectorstore, mock_qa_chain, 
                                 mock_agent, mock_run_chat):
        """Test the complete application flow from main.py"""
        # Mock data loaders
        mock_gmail.return_value = ["Email 1", "Email 2"]
        mock_notion.return_value = ["Page 1", "Page 2"]
        mock_calendar.return_value = ["Event 1", "Event 2"]
        
        # Mock memory components
        mock_vectorstore_instance = MagicMock()
        mock_vectorstore.return_value = mock_vectorstore_instance
        
        mock_qa_chain_instance = MagicMock()
        mock_qa_chain.return_value = mock_qa_chain_instance
        
        mock_agent_instance = MagicMock()
        mock_agent.return_value = mock_agent_instance
        
        # Import and run main
        import main
        
        # Verify the flow
        mock_load_api_keys.assert_called_once()
        mock_gmail.assert_called_once()
        mock_notion.assert_called_once()
        mock_calendar.assert_called_once()
        
        # Verify data aggregation
        expected_all_data = [] + ["Email 1", "Email 2"] + ["Page 1", "Page 2"] + ["Event 1", "Event 2"]
        mock_vectorstore.assert_called_once_with(expected_all_data)
        
        # Verify memory system setup
        mock_qa_chain.assert_called_once_with(mock_vectorstore_instance)
        mock_agent.assert_called_once_with(mock_qa_chain_instance)
        
        # Verify chat interface started
        mock_run_chat.assert_called_once_with(mock_agent_instance)
    
    @patch('loaders.gmail_loader.build')
    @patch('loaders.notion_loader.Client')
    @patch('loaders.calendar_loader.build')
    @patch('memory.vectorstore.FAISS')
    @patch('memory.vectorstore.OpenAIEmbeddings')
    @patch('memory.rag_chain.OpenAI')
    @patch('memory.rag_chain.RetrievalQA')
    @patch('agent.memory_agent.OpenAI')
    @patch('agent.memory_agent.initialize_agent')
    def test_end_to_end_data_flow(self, mock_agent_openai, mock_initialize_agent,
                                mock_rag_openai, mock_retrieval_qa, mock_embeddings,
                                mock_faiss, mock_calendar_build, mock_notion_client,
                                mock_gmail_build):
        """Test end-to-end data flow without mocking main components"""
        with patch.dict(os.environ, self.test_env_vars):
            # Mock external services
            self._setup_gmail_mocks(mock_gmail_build)
            self._setup_notion_mocks(mock_notion_client)
            self._setup_calendar_mocks(mock_calendar_build)
            
            # Mock memory components
            self._setup_memory_mocks(mock_embeddings, mock_faiss, mock_rag_openai, mock_retrieval_qa)
            
            # Mock agent components
            self._setup_agent_mocks(mock_agent_openai, mock_initialize_agent)
            
            # Import modules and test flow
            from loaders.gmail_loader import load_gmail_emails
            from loaders.notion_loader import load_notion_pages
            from loaders.calendar_loader import load_calendar_events
            from memory.vectorstore import build_vectorstore
            from memory.rag_chain import build_qa_chain
            from agent.memory_agent import build_agent
            
            # Execute the flow
            gmail_data = load_gmail_emails()
            notion_data = load_notion_pages()
            calendar_data = load_calendar_events()
            
            all_data = [] + gmail_data + notion_data + calendar_data
            vectorstore = build_vectorstore(all_data)
            qa_chain = build_qa_chain(vectorstore)
            agent = build_agent(qa_chain)
            
            # Verify data was processed
            self.assertIsInstance(gmail_data, list)
            self.assertIsInstance(notion_data, list)
            self.assertIsInstance(calendar_data, list)
            self.assertIsNotNone(vectorstore)
            self.assertIsNotNone(qa_chain)
            self.assertIsNotNone(agent)
    
    def _setup_gmail_mocks(self, mock_build):
        """Setup Gmail API mocks"""
        with patch('loaders.gmail_loader.os.path.exists', return_value=True), \
             patch('loaders.gmail_loader.Credentials') as mock_creds:
            
            mock_creds_instance = MagicMock()
            mock_creds_instance.valid = True
            mock_creds.from_authorized_user_file.return_value = mock_creds_instance
            
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            mock_service.users().messages().list().execute.return_value = {
                'messages': [{'id': '1'}]
            }
            mock_service.users().messages().get().execute.return_value = {
                'snippet': 'Test email'
            }
    
    def _setup_notion_mocks(self, mock_client):
        """Setup Notion API mocks"""
        mock_notion = MagicMock()
        mock_client.return_value = mock_notion
        mock_notion.databases.query.return_value = {
            'results': [{
                'properties': {
                    'Name': {'title': [{'plain_text': 'Test Page'}]}
                }
            }]
        }
    
    def _setup_calendar_mocks(self, mock_build):
        """Setup Calendar API mocks"""
        with patch('loaders.calendar_loader.os.path.exists', return_value=True), \
             patch('loaders.calendar_loader.Credentials') as mock_creds, \
             patch('loaders.calendar_loader.datetime') as mock_datetime:
            
            mock_creds_instance = MagicMock()
            mock_creds_instance.valid = True
            mock_creds.from_authorized_user_file.return_value = mock_creds_instance
            
            mock_datetime.datetime.utcnow().isoformat.return_value = '2024-01-01T00:00:00'
            
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            mock_service.events().list().execute.return_value = {
                'items': [{'summary': 'Test Event'}]
            }
    
    def _setup_memory_mocks(self, mock_embeddings, mock_faiss, mock_openai, mock_retrieval_qa):
        """Setup memory system mocks"""
        with patch('memory.vectorstore.RecursiveCharacterTextSplitter') as mock_splitter:
            mock_splitter_instance = MagicMock()
            mock_splitter.return_value = mock_splitter_instance
            mock_splitter_instance.create_documents.return_value = [MagicMock()]
            
            mock_embeddings_instance = MagicMock()
            mock_embeddings.return_value = mock_embeddings_instance
            
            mock_vectorstore = MagicMock()
            mock_retriever = MagicMock()
            mock_vectorstore.as_retriever.return_value = mock_retriever
            mock_faiss.from_documents.return_value = mock_vectorstore
            
            mock_llm = MagicMock()
            mock_openai.return_value = mock_llm
            
            mock_qa_chain = MagicMock()
            mock_retrieval_qa.from_chain_type.return_value = mock_qa_chain
    
    def _setup_agent_mocks(self, mock_openai, mock_initialize_agent):
        """Setup agent mocks"""
        mock_llm = MagicMock()
        mock_openai.return_value = mock_llm
        
        mock_agent = MagicMock()
        mock_initialize_agent.return_value = mock_agent
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_user_interaction_flow(self, mock_print, mock_input):
        """Test user interaction with the complete system"""
        # Mock user inputs
        mock_input.side_effect = [
            "What emails do I have?",
            "What are my upcoming meetings?",
            "exit"
        ]
        
        # Mock agent responses
        mock_agent = MagicMock()
        mock_agent.run.side_effect = [
            "You have 2 emails about machine learning.",
            "You have a meeting tomorrow at 2 PM."
        ]
        
        from ui.chat_terminal import run_chat
        run_chat(mock_agent)
        
        # Verify interactions
        self.assertEqual(mock_agent.run.call_count, 2)
        mock_agent.run.assert_any_call("What emails do I have?")
        mock_agent.run.assert_any_call("What are my upcoming meetings?")
    
    def test_error_scenarios(self):
        """Test various error scenarios"""
        # Test missing environment variables
        with patch.dict(os.environ, {}, clear=True):
            from config import load_api_keys
            
            # This should not crash but environment variables won't be set
            load_api_keys()
            
            # Verify critical env vars are missing
            self.assertIsNone(os.environ.get('OPENAI_API_KEY'))
    
    @patch('loaders.gmail_loader.build')
    def test_api_failure_handling(self, mock_build):
        """Test handling of API failures"""
        # Mock API failure
        mock_build.side_effect = Exception("API connection failed")
        
        with patch.dict(os.environ, self.test_env_vars):
            from loaders.gmail_loader import load_gmail_emails
            
            # This should raise an exception in current implementation
            with self.assertRaises(Exception):
                load_gmail_emails()


if __name__ == '__main__':
    unittest.main()
