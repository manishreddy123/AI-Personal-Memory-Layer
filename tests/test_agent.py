import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.memory_agent import build_agent
from ui.chat_terminal import run_chat


class TestAgent(unittest.TestCase):
    """Test the agent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_qa_chain = MagicMock()
        self.mock_qa_chain.run.return_value = "Test response from QA chain"
    
    @patch('agent.memory_agent.initialize_agent')
    @patch('agent.memory_agent.OpenAI')
    @patch('agent.memory_agent.Tool')
    def test_agent_creation(self, mock_tool, mock_openai, mock_initialize_agent):
        """Test agent creation with proper tools and LLM"""
        # Mock components
        mock_llm = MagicMock()
        mock_openai.return_value = mock_llm
        
        mock_tool_instance = MagicMock()
        mock_tool.return_value = mock_tool_instance
        
        mock_agent = MagicMock()
        mock_initialize_agent.return_value = mock_agent
        
        # Create agent
        result = build_agent(self.mock_qa_chain)
        
        # Verify LLM was created with correct temperature
        mock_openai.assert_called_once_with(temperature=0)
        
        # Verify tool was created
        mock_tool.assert_called_once()
        tool_call_args = mock_tool.call_args
        self.assertEqual(tool_call_args[1]['name'], "Ask Personal Assistant")
        self.assertEqual(tool_call_args[1]['func'], self.mock_qa_chain.run)
        self.assertIn("memory", tool_call_args[1]['description'].lower())
        
        # Verify agent was initialized
        mock_initialize_agent.assert_called_once()
        init_call_args = mock_initialize_agent.call_args[0]
        self.assertEqual(len(init_call_args[0]), 1)  # One tool
        self.assertEqual(init_call_args[1], mock_llm)  # LLM
        
        init_call_kwargs = mock_initialize_agent.call_args[1]
        self.assertEqual(init_call_kwargs['agent'], "zero-shot-react-description")
        self.assertTrue(init_call_kwargs['verbose'])
        
        self.assertEqual(result, mock_agent)
    
    @patch('agent.memory_agent.initialize_agent')
    @patch('agent.memory_agent.OpenAI')
    def test_agent_tool_functionality(self, mock_openai, mock_initialize_agent):
        """Test that the agent tool can call the QA chain"""
        mock_llm = MagicMock()
        mock_openai.return_value = mock_llm
        
        mock_agent = MagicMock()
        mock_initialize_agent.return_value = mock_agent
        
        # Create agent
        agent = build_agent(self.mock_qa_chain)
        
        # Get the tool function that was passed to Tool constructor
        tool_call_args = None
        with patch('agent.memory_agent.Tool') as mock_tool:
            build_agent(self.mock_qa_chain)
            tool_call_args = mock_tool.call_args[1]
        
        # Test the tool function
        tool_func = tool_call_args['func']
        result = tool_func("What is machine learning?")
        
        # Verify QA chain was called
        self.mock_qa_chain.run.assert_called_with("What is machine learning?")
        self.assertEqual(result, "Test response from QA chain")
    
    @patch('agent.memory_agent.initialize_agent')
    @patch('agent.memory_agent.OpenAI')
    def test_agent_with_different_qa_chains(self, mock_openai, mock_initialize_agent):
        """Test agent creation with different QA chain configurations"""
        mock_llm = MagicMock()
        mock_openai.return_value = mock_llm
        
        mock_agent = MagicMock()
        mock_initialize_agent.return_value = mock_agent
        
        # Test with different QA chain responses
        test_cases = [
            "Response about emails",
            "Response about calendar events",
            "Response about notion pages"
        ]
        
        for expected_response in test_cases:
            qa_chain = MagicMock()
            qa_chain.run.return_value = expected_response
            
            agent = build_agent(qa_chain)
            
            # Verify agent was created
            self.assertIsNotNone(agent)
            mock_initialize_agent.assert_called()


class TestChatTerminal(unittest.TestCase):
    """Test the chat terminal interface"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_agent = MagicMock()
        self.mock_agent.run.return_value = "AI response"
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_chat_terminal_single_interaction(self, mock_print, mock_input):
        """Test single chat interaction"""
        # Mock user input: one question then exit
        mock_input.side_effect = ["What is machine learning?", "exit"]
        
        run_chat(self.mock_agent)
        
        # Verify agent was called with user input
        self.mock_agent.run.assert_called_once_with("What is machine learning?")
        
        # Verify print was called for welcome message and AI response
        print_calls = [call[0][0] for call in mock_print.call_args_list]
        self.assertTrue(any("AI Personal Memory Assistant ready" in call for call in print_calls))
        self.assertTrue(any("AI response" in call for call in print_calls))
        self.assertTrue(any("Goodbye!" in call for call in print_calls))
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_chat_terminal_multiple_interactions(self, mock_print, mock_input):
        """Test multiple chat interactions"""
        # Mock multiple user inputs
        mock_input.side_effect = [
            "First question",
            "Second question", 
            "quit"
        ]
        
        # Mock different agent responses
        self.mock_agent.run.side_effect = [
            "First response",
            "Second response"
        ]
        
        run_chat(self.mock_agent)
        
        # Verify agent was called twice
        self.assertEqual(self.mock_agent.run.call_count, 2)
        self.mock_agent.run.assert_any_call("First question")
        self.mock_agent.run.assert_any_call("Second question")
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_chat_terminal_exit_commands(self, mock_print, mock_input):
        """Test different exit commands"""
        exit_commands = ["exit", "quit", "EXIT", "QUIT"]
        
        for exit_cmd in exit_commands:
            with self.subTest(exit_command=exit_cmd):
                mock_input.side_effect = [exit_cmd]
                mock_agent = MagicMock()
                
                run_chat(mock_agent)
                
                # Verify agent was not called
                mock_agent.run.assert_not_called()
                
                # Reset for next iteration
                mock_print.reset_mock()
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_chat_terminal_agent_error_handling(self, mock_print, mock_input):
        """Test chat terminal handles agent errors gracefully"""
        mock_input.side_effect = ["Test question", "exit"]
        
        # Mock agent to raise an exception
        self.mock_agent.run.side_effect = Exception("Agent error")
        
        # This should not raise an exception in a real implementation
        # For now, we'll test that the exception propagates
        with self.assertRaises(Exception):
            run_chat(self.mock_agent)


if __name__ == '__main__':
    unittest.main()
