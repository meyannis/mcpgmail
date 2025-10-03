#!/usr/bin/env python3
"""
Enhanced Gmail API Utilities

This module provides comprehensive functions for interacting with the Gmail API.
"""

import base64
import logging
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError
from typing import Dict, List, Optional, Any, Union

# Set up logging
logger = logging.getLogger("gmail_api")

def get_profile(service, user_id='me'):
    """
    Get user profile information
    
    Args:
        service: Gmail API service instance
        user_id: User's email address (default: 'me')
    
    Returns:
        User profile data
    """
    try:
        profile = service.users().getProfile(userId=user_id).execute()
        return profile
    
    except HttpError as error:
        logger.error(f'Error getting profile: {error}')
        return None

def list_messages(service, user_id='me', max_results=10, query=None):
    """
    List email message IDs from Gmail inbox
    
    Args:
        service: Gmail API service instance
        user_id: User's email address (default: 'me')
        max_results: Maximum number of results to return
        query: Optional search query
    
    Returns:
        List of message IDs
    """
    try:
        # Build request parameters
        params = {
            'userId': user_id, 
            'maxResults': max_results
        }
        
        if query:
            params['q'] = query
            
        response = service.users().messages().list(**params).execute()
        
        messages = response.get('messages', [])
        return [msg['id'] for msg in messages]
    
    except HttpError as error:
        logger.error(f'Error listing messages: {error}')
        return []

def get_message(service, msg_id, user_id='me', format='metadata'):
    """
    Get a specific message by ID
    
    Args:
        service: Gmail API service instance
        msg_id: The message ID
        user_id: User's email address (default: 'me')
        format: Format to return the message in ('full', 'metadata', 'minimal', 'raw')
    
    Returns:
        The message data
    """
    try:
        message = service.users().messages().get(
            userId=user_id, 
            id=msg_id, 
            format=format
        ).execute()
        
        return message
    
    except HttpError as error:
        logger.error(f'Error getting message {msg_id}: {error}')
        raise

def search_messages(service, query, max_results=10, user_id='me'):
    """
    Search for messages matching a query
    
    Args:
        service: Gmail API service instance
        query: Gmail search query string (using Gmail's search syntax)
        max_results: Maximum number of results to return
        user_id: User's email address (default: 'me')
    
    Returns:
        List of message IDs matching the query
    """
    try:
        response = service.users().messages().list(
            userId=user_id,
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = response.get('messages', [])
        return [msg['id'] for msg in messages]
    
    except HttpError as error:
        logger.error(f'Error searching messages: {error}')
        return []

def list_drafts(service, max_results=10, user_id='me'):
    """
    List email drafts
    
    Args:
        service: Gmail API service instance
        max_results: Maximum number of results to return
        user_id: User's email address (default: 'me')
    
    Returns:
        List of draft data
    """
    try:
        response = service.users().drafts().list(
            userId=user_id,
            maxResults=max_results
        ).execute()
        
        return response
    
    except HttpError as error:
        logger.error(f'Error listing drafts: {error}')
        return {'drafts': []}

def get_draft(service, draft_id, user_id='me'):
    """
    Get a specific draft by ID
    
    Args:
        service: Gmail API service instance
        draft_id: The draft ID
        user_id: User's email address (default: 'me')
    
    Returns:
        The draft data
    """
    try:
        draft = service.users().drafts().get(
            userId=user_id,
            id=draft_id
        ).execute()
        
        return draft
    
    except HttpError as error:
        logger.error(f'Error getting draft {draft_id}: {error}')
        return None

def create_draft(service, message, user_id='me'):
    """
    Create an email draft
    
    Args:
        service: Gmail API service instance
        message: The email message dictionary
        user_id: User's email address (default: 'me')
    
    Returns:
        The created draft data
    """
    try:
        draft = service.users().drafts().create(
            userId=user_id,
            body={'message': message}
        ).execute()
        
        return draft
    
    except HttpError as error:
        logger.error(f'Error creating draft: {error}')
        raise

def update_draft(service, draft_id, message, user_id='me'):
    """
    Update an existing draft
    
    Args:
        service: Gmail API service instance
        draft_id: The draft ID to update
        message: The updated email message dictionary
        user_id: User's email address (default: 'me')
    
    Returns:
        The updated draft data
    """
    try:
        draft = service.users().drafts().update(
            userId=user_id,
            id=draft_id,
            body={'message': message}
        ).execute()
        
        return draft
    
    except HttpError as error:
        logger.error(f'Error updating draft {draft_id}: {error}')
        raise

def send_message(service, message, user_id='me'):
    """
    Send an email message
    
    Args:
        service: Gmail API service instance
        message: The email message dictionary
        user_id: User's email address (default: 'me')
    
    Returns:
        The sent message data
    """
    try:
        message = service.users().messages().send(
            userId=user_id,
            body=message
        ).execute()
        
        return message
    
    except HttpError as error:
        logger.error(f'Error sending message: {error}')
        raise

def delete_message(service, msg_id, user_id='me'):
    """
    Move a message to trash
    
    Args:
        service: Gmail API service instance
        msg_id: The message ID
        user_id: User's email address (default: 'me')
    """
    try:
        service.users().messages().trash(
            userId=user_id,
            id=msg_id
        ).execute()
        
        return True
    
    except HttpError as error:
        logger.error(f'Error deleting message {msg_id}: {error}')
        raise

def permanently_delete_message(service, msg_id, user_id='me'):
    """
    Permanently delete a message (skipping trash)
    
    Args:
        service: Gmail API service instance
        msg_id: The message ID
        user_id: User's email address (default: 'me')
    """
    try:
        service.users().messages().delete(
            userId=user_id,
            id=msg_id
        ).execute()
        
        return True
    
    except HttpError as error:
        logger.error(f'Error permanently deleting message {msg_id}: {error}')
        raise

def modify_message(service, msg_id, modifications, user_id='me'):
    """
    Modify message labels
    
    Args:
        service: Gmail API service instance
        msg_id: The message ID
        modifications: Dict with addLabelIds and/or removeLabelIds fields
        user_id: User's email address (default: 'me')
    
    Returns:
        The modified message
    """
    try:
        result = service.users().messages().modify(
            userId=user_id,
            id=msg_id,
            body=modifications
        ).execute()
        
        return result
    
    except HttpError as error:
        logger.error(f'Error modifying message {msg_id}: {error}')
        raise

def batch_modify_messages(service, msg_ids, modifications, user_id='me'):
    """
    Batch modify multiple messages' labels
    
    Args:
        service: Gmail API service instance
        msg_ids: List of message IDs
        modifications: Dict with addLabelIds and/or removeLabelIds fields
        user_id: User's email address (default: 'me')
    """
    try:
        result = service.users().messages().batchModify(
            userId=user_id,
            body={
                'ids': msg_ids,
                **modifications
            }
        ).execute()
        
        return result
    
    except HttpError as error:
        logger.error(f'Error batch modifying messages: {error}')
        raise

def get_labels(service, user_id='me'):
    """
    Get all labels for a user
    
    Args:
        service: Gmail API service instance
        user_id: User's email address (default: 'me')
    
    Returns:
        List of label objects
    """
    try:
        response = service.users().labels().list(userId=user_id).execute()
        return response.get('labels', [])
    
    except HttpError as error:
        logger.error(f'Error getting labels: {error}')
        return []

def get_label(service, label_id, user_id='me'):
    """
    Get a specific label by ID
    
    Args:
        service: Gmail API service instance
        label_id: The label ID
        user_id: User's email address (default: 'me')
    
    Returns:
        The label object
    """
    try:
        label = service.users().labels().get(
            userId=user_id,
            id=label_id
        ).execute()
        
        return label
    
    except HttpError as error:
        logger.error(f'Error getting label {label_id}: {error}')
        return None

def create_label(service, name, user_id='me'):
    """
    Create a new label
    
    Args:
        service: Gmail API service instance
        name: The name of the new label
        user_id: User's email address (default: 'me')
    
    Returns:
        The created label object
    """
    try:
        label = service.users().labels().create(
            userId=user_id,
            body={
                'name': name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
        ).execute()
        
        return label
    
    except HttpError as error:
        logger.error(f'Error creating label {name}: {error}')
        raise

def update_label(service, label_id, updates, user_id='me'):
    """
    Update an existing label
    
    Args:
        service: Gmail API service instance
        label_id: The ID of the label to update
        updates: Dict with updated label fields
        user_id: User's email address (default: 'me')
    
    Returns:
        The updated label object
    """
    try:
        label = service.users().labels().patch(
            userId=user_id,
            id=label_id,
            body=updates
        ).execute()
        
        return label
    
    except HttpError as error:
        logger.error(f'Error updating label {label_id}: {error}')
        raise

def delete_label(service, label_id, user_id='me'):
    """
    Delete a label
    
    Args:
        service: Gmail API service instance
        label_id: The ID of the label to delete
        user_id: User's email address (default: 'me')
    """
    try:
        service.users().labels().delete(
            userId=user_id,
            id=label_id
        ).execute()
        
        return True
    
    except HttpError as error:
        logger.error(f'Error deleting label {label_id}: {error}')
        raise

def apply_label(service, msg_id, label_id, user_id='me'):
    """
    Apply a label to a message
    
    Args:
        service: Gmail API service instance
        msg_id: The message ID
        label_id: The label ID
        user_id: User's email address (default: 'me')
    """
    try:
        result = service.users().messages().modify(
            userId=user_id,
            id=msg_id,
            body={'addLabelIds': [label_id]}
        ).execute()
        
        return result
    
    except HttpError as error:
        logger.error(f'Error applying label {label_id} to message {msg_id}: {error}')
        raise

def remove_label(service, msg_id, label_id, user_id='me'):
    """
    Remove a label from a message
    
    Args:
        service: Gmail API service instance
        msg_id: The message ID
        label_id: The label ID
        user_id: User's email address (default: 'me')
    """
    try:
        result = service.users().messages().modify(
            userId=user_id,
            id=msg_id,
            body={'removeLabelIds': [label_id]}
        ).execute()
        
        return result
    
    except HttpError as error:
        logger.error(f'Error removing label {label_id} from message {msg_id}: {error}')
        raise

def get_thread(service, thread_id, user_id='me'):
    """
    Get a thread by ID
    
    Args:
        service: Gmail API service instance
        thread_id: The thread ID
        user_id: User's email address (default: 'me')
    
    Returns:
        The thread data
    """
    try:
        thread = service.users().threads().get(
            userId=user_id,
            id=thread_id
        ).execute()
        
        return thread
    
    except HttpError as error:
        logger.error(f'Error getting thread {thread_id}: {error}')
        return None

def list_threads(service, query=None, max_results=10, user_id='me'):
    """
    List email threads
    
    Args:
        service: Gmail API service instance
        query: Optional search query
        max_results: Maximum number of results to return
        user_id: User's email address (default: 'me')
    
    Returns:
        List of thread data
    """
    try:
        params = {
            'userId': user_id,
            'maxResults': max_results
        }
        
        if query:
            params['q'] = query
            
        response = service.users().threads().list(**params).execute()
        
        return response.get('threads', [])
    
    except HttpError as error:
        logger.error(f'Error listing threads: {error}')
        return []

def get_attachment(service, message_id, attachment_id, user_id='me'):
    """
    Get an attachment by ID
    
    Args:
        service: Gmail API service instance
        message_id: The message ID
        attachment_id: The attachment ID
        user_id: User's email address (default: 'me')
    
    Returns:
        The attachment data
    """
    try:
        attachment = service.users().messages().attachments().get(
            userId=user_id,
            messageId=message_id,
            id=attachment_id
        ).execute()
        
        # The attachment is base64 encoded
        data = attachment['data']
        file_data = base64.urlsafe_b64decode(data)
        
        return file_data
    
    except HttpError as error:
        logger.error(f'Error getting attachment {attachment_id} from message {message_id}: {error}')
        return None

def import_message(service, message_content, user_id='me'):
    """
    Import a message directly into a mailbox
    
    Args:
        service: Gmail API service instance
        message_content: Raw message content
        user_id: User's email address (default: 'me')
    
    Returns:
        The imported message data
    """
    try:
        # Ensure message_content is base64 encoded
        if isinstance(message_content, str):
            message_content = message_content.encode('utf-8')
            
        encoded_message = base64.urlsafe_b64encode(message_content).decode('utf-8')
        
        result = service.users().messages().import_(
            userId=user_id,
            body={
                'raw': encoded_message
            }
        ).execute()
        
        return result
    
    except HttpError as error:
        logger.error(f'Error importing message: {error}')
        raise

def forward_message(service, message_id, to, user_id='me'):
    """
    Forward a message to another recipient
    
    Args:
        service: Gmail API service instance
        message_id: The message ID to forward
        to: The recipient email address
        user_id: User's email address (default: 'me')
    
    Returns:
        The sent message data
    """
    try:
        # Get the original message
        message = get_message(service, message_id, user_id=user_id, format='raw')
        
        # Decode the raw message
        raw_message = base64.urlsafe_b64decode(message['raw']).decode('utf-8')
        
        # Create a MIMEText with the forwarded message
        forward = MIMEText(raw_message, 'rfc822')
        forward['To'] = to
        forward['Subject'] = f"Fwd: {get_message_subject(message)}"
        
        # Encode the message
        encoded_message = base64.urlsafe_b64encode(forward.as_string().encode('utf-8')).decode('utf-8')
        
        # Send the forwarded message
        result = send_message(service, {'raw': encoded_message}, user_id=user_id)
        
        return result
    
    except HttpError as error:
        logger.error(f'Error forwarding message {message_id}: {error}')
        raise

def get_message_subject(message):
    """
    Extract the subject from a message
    
    Args:
        message: The message object
    
    Returns:
        The subject string
    """
    if 'payload' in message and 'headers' in message['payload']:
        for header in message['payload']['headers']:
            if header['name'].lower() == 'subject':
                return header['value']
    
    return "No Subject"
