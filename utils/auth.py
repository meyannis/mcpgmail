#!/usr/bin/env python3
"""
Enhanced Gmail API Authentication Utilities

This module handles OAuth 2.0 authentication for the Gmail API with improved
token management, security, and error handling.
"""

import os
import logging
import json
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Set up logging
logger = logging.getLogger("gmail_auth")

# If modifying these scopes, delete the token.json file.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.labels'
]

# Default file paths
DEFAULT_CREDENTIALS_PATH = 'credentials.json'
DEFAULT_TOKEN_PATH = 'token.json'

def get_token_path():
    """
    Get token path from environment variable or use default
    
    Returns:
        Path to token file
    """
    return os.environ.get('GMAIL_TOKEN_PATH', DEFAULT_TOKEN_PATH)

def get_credentials_path():
    """
    Get credentials path from environment variable or use default
    
    Returns:
        Path to credentials file
    """
    return os.environ.get('GMAIL_CREDENTIALS_PATH', DEFAULT_CREDENTIALS_PATH)

def load_credentials():
    """
    Load OAuth2 credentials from file or environment variables
    
    Returns:
        Client ID and client secret as tuple
    """
    # Try to get credentials from environment variables first
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    if client_id and client_secret:
        logger.info("Using credentials from environment variables")
        return client_id, client_secret
    
    # Otherwise, try to load from credentials file
    credentials_path = get_credentials_path()
    
    try:
        with open(credentials_path, 'r') as f:
            credentials_data = json.load(f)
            
        if 'installed' in credentials_data:
            client_id = credentials_data['installed']['client_id']
            client_secret = credentials_data['installed']['client_secret']
            return client_id, client_secret
        elif 'web' in credentials_data:
            client_id = credentials_data['web']['client_id']
            client_secret = credentials_data['web']['client_secret']
            return client_id, client_secret
        else:
            logger.error(f"Unexpected credentials format in {credentials_path}")
            return None, None
            
    except FileNotFoundError:
        logger.error(f"Credentials file not found: {credentials_path}")
        return None, None
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in credentials file: {credentials_path}")
        return None, None
    except Exception as e:
        logger.error(f"Error loading credentials: {str(e)}")
        return None, None

def get_gmail_service():
    """
    Authenticate and return a Gmail API service instance.
    
    This function handles the OAuth 2.0 flow for Gmail API authentication.
    It looks for existing credentials in token.json, refreshes them if needed,
    or initiates a new authentication flow if no valid credentials exist.
    
    Returns:
        A Gmail API service instance
    """
    creds = None
    token_path = get_token_path()
    
    try:
        # The file token.json stores the user's access and refresh tokens
        if os.path.exists(token_path):
            logger.info(f"Loading existing token from {token_path}")
            
            try:
                with open(token_path, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                logger.warning(f"Failed to load token from {token_path}: {str(e)}")
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired credentials")
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.warning(f"Error refreshing credentials: {str(e)}")
                    creds = None
            
            # If still no valid credentials, initiate OAuth flow
            if not creds:
                logger.info("Initiating OAuth authentication flow")
                
                # Load client secrets from credentials.json file
                credentials_path = get_credentials_path()
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                except FileNotFoundError:
                    raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
                
                # Run local server to handle auth flow
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            try:
                # Create directory if it doesn't exist
                token_dir = os.path.dirname(token_path)
                if token_dir and not os.path.exists(token_dir):
                    os.makedirs(token_dir)
                    
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
                logger.info(f"Saved authentication token to {token_path}")
            except Exception as e:
                logger.warning(f"Failed to save token to {token_path}: {str(e)}")
        
        # Build the Gmail service
        try:
            service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API service created successfully")
            return service
        except Exception as e:
            logger.error(f"Error building Gmail service: {str(e)}")
            raise
    
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise
