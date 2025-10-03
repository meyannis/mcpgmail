#!/usr/bin/env python3
"""
Tests for the Gmail MCP Server
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for importing server modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gmail_server import send_email, search_emails, read_email


class TestGmailServer(unittest.TestCase):
    """Test cases for Gmail MCP Server functions"""
    
    @patch('gmail_server.get_gmail_service')
    @patch('gmail_server.send_message')
    def test_send_email(self, mock_send_message, mock_get_service):
        """Test sending an email"""
        # Setup mocks
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_send_message.return_value = {'id': 'msg123'}
        
        # Call the function (we need to handle the async function)
        import asyncio
        result = asyncio.run(send_email(
            to='test@example.com',
            subject='Test Subject',
            body='Test Body'
        ))
        
        # Assertions
        mock_get_service.assert_called_once()
        mock_send_message.assert_called_once()
        self.assertIn('Email sent successfully', result)
        self.assertIn('msg123', result)

    @patch('gmail_server.get_gmail_service')
    @patch('gmail_server.search_messages')
    @patch('gmail_server.get_message')
    def test_search_emails(self, mock_get_message, mock_search_messages, mock_get_service):
        """Test searching emails"""
        # Setup mocks
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_search_messages.return_value = ['msg1', 'msg2']
        
        # Mock message data
        mock_message1 = {
            'id': 'msg1',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject 1'},
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'Date', 'value': '2023-01-01'}
                ]
            }
        }
        mock_message2 = {
            'id': 'msg2',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject 2'},
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'Date', 'value': '2023-01-02'}
                ]
            }
        }
        
        # Configure get_message to return different messages
        mock_get_message.side_effect = [mock_message1, mock_message2]
        
        # Call the function
        import asyncio
        result = asyncio.run(search_emails('test query', 2))
        
        # Assertions
        mock_get_service.assert_called_once()
        mock_search_messages.assert_called_once_with(mock_service, 'test query', 2)
        self.assertEqual(mock_get_message.call_count, 2)
        self.assertIn('Test Subject 1', result)
        self.assertIn('Test Subject 2', result)

    @patch('gmail_server.get_gmail_service')
    @patch('gmail_server.get_message')
    def test_read_email(self, mock_get_message, mock_get_service):
        """Test reading an email"""
        # Setup mocks
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        
        # Create a test email with encoded body
        import base64
        test_body = "This is a test email body."
        encoded_body = base64.urlsafe_b64encode(test_body.encode()).decode()
        
        mock_email = {
            'id': 'msg1',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'From', 'value': 'sender@example.com'},
                    {'name': 'To', 'value': 'recipient@example.com'},
                    {'name': 'Date', 'value': '2023-01-01'}
                ],
                'body': {
                    'data': encoded_body
                }
            }
        }
        
        mock_get_message.return_value = mock_email
        
        # Call the function
        import asyncio
        result = asyncio.run(read_email('msg1'))
        
        # Assertions
        mock_get_service.assert_called_once()
        mock_get_message.assert_called_once_with(mock_service, 'msg1', format='full')
        self.assertIn('Test Subject', result)
        self.assertIn('sender@example.com', result)
        self.assertIn('recipient@example.com', result)
        self.assertIn(test_body, result)


if __name__ == '__main__':
    unittest.main()
