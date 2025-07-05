import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loaders.gmail_loader import load_gmail_emails
from loaders.notion_loader import load_notion_pages
from loaders.calendar_loader import load_calendar_events


class TestLoaders(unittest.TestCase):
    """Test all data loaders"""
    
    @patch('loaders.gmail_loader.build')
    @patch('loaders.gmail_loader.Credentials')
    @patch('loaders.gmail_loader.os.path.exists')
    @patch.dict(os.environ, {'GOOGLE_CLIENT_SECRET_FILE': 'test_credentials.json'})
    def test_gmail_loader_with_existing_token(self, mock_exists, mock_credentials, mock_build):
        """Test Gmail loader with existing token"""
        # Mock existing token
        mock_exists.return_value = True
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        
        # Mock Gmail service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Mock Gmail API responses
        mock_service.users().messages().list().execute.return_value = {
            'messages': [{'id': '1'}, {'id': '2'}]
        }
        mock_service.users().messages().get().execute.return_value = {
            'snippet': 'Test email snippet'
        }
        
        result = load_gmail_emails()
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], 'Test email snippet')
    
    @patch('loaders.gmail_loader.build')
    @patch('loaders.gmail_loader.InstalledAppFlow')
    @patch('loaders.gmail_loader.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch.dict(os.environ, {'GOOGLE_CLIENT_SECRET_FILE': 'test_credentials.json'})
    def test_gmail_loader_without_token(self, mock_file, mock_exists, mock_flow, mock_build):
        """Test Gmail loader without existing token"""
        # Mock no existing token
        mock_exists.return_value = False
        
        # Mock OAuth flow
        mock_flow_instance = MagicMock()
        mock_creds = MagicMock()
        mock_creds.to_json.return_value = '{"token": "test"}'
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.from_client_secrets_file.return_value = mock_flow_instance
        
        # Mock Gmail service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.users().messages().list().execute.return_value = {'messages': []}
        
        result = load_gmail_emails()
        
        self.assertIsInstance(result, list)
        mock_flow.from_client_secrets_file.assert_called_once()
    
    @patch('loaders.notion_loader.Client')
    @patch.dict(os.environ, {
        'NOTION_API_KEY': 'test_notion_key',
        'NOTION_DB_ID': 'test_db_id'
    })
    def test_notion_loader_success(self, mock_client):
        """Test Notion loader success case"""
        # Mock Notion client
        mock_notion = MagicMock()
        mock_client.return_value = mock_notion
        
        # Mock Notion API response
        mock_notion.databases.query.return_value = {
            'results': [
                {
                    'properties': {
                        'Name': {
                            'title': [{'plain_text': 'Test Page 1'}]
                        }
                    }
                },
                {
                    'properties': {
                        'Name': {
                            'title': [{'plain_text': 'Test Page 2'}]
                        }
                    }
                }
            ]
        }
        
        result = load_notion_pages()
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], 'Test Page 1')
        self.assertEqual(result[1], 'Test Page 2')
    
    @patch('loaders.notion_loader.Client')
    @patch.dict(os.environ, {
        'NOTION_API_KEY': 'test_notion_key',
        'NOTION_DB_ID': 'test_db_id'
    })
    def test_notion_loader_empty_response(self, mock_client):
        """Test Notion loader with empty response"""
        mock_notion = MagicMock()
        mock_client.return_value = mock_notion
        mock_notion.databases.query.return_value = {'results': []}
        
        result = load_notion_pages()
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    @patch('loaders.calendar_loader.build')
    @patch('loaders.calendar_loader.Credentials')
    @patch('loaders.calendar_loader.os.path.exists')
    @patch('loaders.calendar_loader.datetime')
    @patch.dict(os.environ, {'GOOGLE_CLIENT_SECRET_FILE': 'test_credentials.json'})
    def test_calendar_loader_success(self, mock_datetime, mock_exists, mock_credentials, mock_build):
        """Test Calendar loader success case"""
        # Mock existing token
        mock_exists.return_value = True
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_credentials.from_authorized_user_file.return_value = mock_creds
        
        # Mock datetime
        mock_datetime.datetime.utcnow().isoformat.return_value = '2024-01-01T00:00:00'
        
        # Mock Calendar service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Mock Calendar API response
        mock_service.events().list().execute.return_value = {
            'items': [
                {'summary': 'Meeting 1'},
                {'summary': 'Meeting 2'},
                {}  # Event without summary
            ]
        }
        
        result = load_calendar_events()
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], 'Meeting 1')
        self.assertEqual(result[1], 'Meeting 2')
        self.assertEqual(result[2], 'No title')
    
    def test_error_handling(self):
        """Test error handling in loaders"""
        # Test with missing environment variables
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises((KeyError, AttributeError)):
                load_notion_pages()


if __name__ == '__main__':
    unittest.main()
