"""Tests for the main module."""

import unittest
from unittest.mock import patch, MagicMock
import os

# Import the main function to test
from src.python_ai_bot.main import main


class TestMain(unittest.TestCase):
    """Test case for the main module."""
    
    @patch('src.python_ai_bot.main.OpenAIClient')
    def test_main(self, mock_client_class):
        """Test the main function with mocked OpenAI client."""
        # Set up the mock
        mock_instance = MagicMock()
        mock_instance.generate_text.return_value = "This is a mocked response"
        mock_client_class.return_value = mock_instance
        
        # Call the function to test
        result = main("Test prompt")
        
        # Check the results
        self.assertEqual(result, "This is a mocked response")
        
        # Verify the client was called with the right parameters
        mock_instance.generate_text.assert_called_once_with("Test prompt")


if __name__ == "__main__":
    unittest.main()
