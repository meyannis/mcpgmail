#!/usr/bin/env python3
"""
Enhanced Gmail MCP Server - Complete Implementation

This MCP server provides a comprehensive set of tools for Claude to interact with Gmail,
allowing it to send emails, search inbox, read messages, manage drafts, labels, and more.

Features:
- Send plain text and HTML emails with attachments
- Search Gmail with powerful query syntax
- Read and parse complex email structures
- Manage drafts, labels, and email organization
- Batch operations for productivity

Author: Your Name
License: MIT
"""

import os
import json
import base64
import re
import logging
import mimetypes
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.header import decode_header
from datetime import datetime, timedelta
import asyncio
import time

from mcp.server.fastmcp import FastMCP, Context
from utils.auth import get_gmail_service
from utils.gmail_api import (
    list_messages,
    get_message,
    search_messages,
    create_draft,
    update_draft,
    send_message,
    delete_message,
    get_draft,
    list_drafts,
    get_labels,
    create_label,
    delete_label,
    apply_label,
    remove_label,
    modify_message,
    get_profile
)
from googleapiclient.errors import HttpError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("gmail_mcp.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("gmail_mcp")

# Initialize FastMCP server with comprehensive dependencies
mcp = FastMCP(
    "Gmail Integration", 
    dependencies=[
        "google-api-python-client>=2.107.0", 
        "google-auth-httplib2>=0.1.0", 
        "google-auth-oauthlib>=1.1.0",
        "mcp>=1.5.0"
    ]
)

@dataclass
class EmailAttachment:
    """Represents an email attachment"""
    filename: str
    content: bytes  # Binary content
    content_id: Optional[str] = None  # For inline images
    mimetype: Optional[str] = None

    def __post_init__(self):
        """Set mimetype based on filename if not specified"""
        if not self.mimetype:
            self.mimetype = mimetypes.guess_type(self.filename)[0] or "application/octet-stream"

@mcp.tool()
async def send_email(
    to: str, 
    subject: str, 
    body: str, 
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html_body: Optional[str] = None,
    importance: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    Send an email using Gmail
    
    Args:
        to: Email recipient(s). Can be a single email or comma-separated list
        subject: Email subject line
        body: Plain text email body content
        cc: Optional carbon copy recipient(s)
        bcc: Optional blind carbon copy recipient(s)
        html_body: Optional HTML version of the email body
        importance: Optional email importance ("high", "normal", "low")
        ctx: MCP Context (automatically injected)
    
    Returns:
        Message confirming email was sent and the message ID
    """
    try:
        if ctx:
            ctx.info(f"Preparing to send email to {to}")
            
        service = get_gmail_service()
        
        # Get user profile to use as From address
        profile = get_profile(service)
        from_email = profile.get('emailAddress', '')
        
        # Create email message
        message = MIMEMultipart('alternative')
        message['To'] = to
        message['Subject'] = subject
        message['From'] = from_email
        
        if cc:
            message['Cc'] = cc
            
        if bcc:
            message['Bcc'] = bcc
        
        # Set importance if specified
        if importance:
            if importance.lower() == "high":
                message['Importance'] = 'high'
                message['X-Priority'] = '1'
            elif importance.lower() == "low":
                message['Importance'] = 'low'
                message['X-Priority'] = '5'
        
        # Attach plain text version
        message.attach(MIMEText(body, 'plain'))
        
        # Attach HTML version if provided
        if html_body:
            message.attach(MIMEText(html_body, 'html'))
        
        # Convert message to string and then to base64 URL-safe string
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Create message dict for Gmail API
        message_dict = {
            'raw': encoded_message
        }
        
        # Send the message
        if ctx:
            ctx.info("Sending email...")
            
        message_result = send_message(service, message_dict)
        
        if ctx:
            ctx.info(f"Email sent successfully with ID: {message_result['id']}")
            
        return f"Email sent successfully to {to}.\nSubject: {subject}\nMessage ID: {message_result['id']}"
    
    except Exception as e:
        error_msg = f"Error sending email: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def send_email_with_attachment(
    to: str, 
    subject: str, 
    body: str, 
    attachment_path: str,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html_body: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    Send an email with an attachment using Gmail
    
    Args:
        to: Email recipient(s). Can be a single email or comma-separated list
        subject: Email subject line
        body: Plain text email body content
        attachment_path: Path to a file to attach
        cc: Optional carbon copy recipient(s)
        bcc: Optional blind carbon copy recipient(s)
        html_body: Optional HTML version of the email body
        ctx: MCP Context (automatically injected)
    
    Returns:
        Message confirming email was sent and the message ID
    """
    try:
        if ctx:
            ctx.info(f"Preparing to send email with attachment to {to}")
            
        service = get_gmail_service()
        
        # Get user profile to use as From address
        profile = get_profile(service)
        from_email = profile.get('emailAddress', '')
        
        # Create email message
        message = MIMEMultipart('mixed')
        message['To'] = to
        message['Subject'] = subject
        message['From'] = from_email
        
        if cc:
            message['Cc'] = cc
            
        if bcc:
            message['Bcc'] = bcc
        
        # Create the message body as multipart/alternative
        msgAlternative = MIMEMultipart('alternative')
        message.attach(msgAlternative)
        
        # Attach plain text version
        msgAlternative.attach(MIMEText(body, 'plain'))
        
        # Attach HTML version if provided
        if html_body:
            msgAlternative.attach(MIMEText(html_body, 'html'))
        
        # Attach file if path is valid
        if os.path.isfile(attachment_path):
            filename = os.path.basename(attachment_path)
            
            if ctx:
                ctx.info(f"Attaching file: {filename}")
                
            with open(attachment_path, 'rb') as file:
                part = MIMEApplication(file.read(), Name=filename)
                part['Content-Disposition'] = f'attachment; filename="{filename}"'
                message.attach(part)
        else:
            error_msg = f"Error: Attachment file not found at path {attachment_path}"
            if ctx:
                ctx.error(error_msg)
            return error_msg
        
        # Convert message to string and then to base64 URL-safe string
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Create message dict for Gmail API
        message_dict = {
            'raw': encoded_message
        }
        
        # Send the message
        if ctx:
            ctx.info("Sending email with attachment...")
            
        message_result = send_message(service, message_dict)
        
        if ctx:
            ctx.info(f"Email sent successfully with ID: {message_result['id']}")
            
        return f"Email with attachment '{filename}' sent successfully to {to}.\nSubject: {subject}\nMessage ID: {message_result['id']}"
    
    except Exception as e:
        error_msg = f"Error sending email with attachment: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def send_email_with_multiple_attachments(
    to: str, 
    subject: str, 
    body: str, 
    attachment_paths: List[str],
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html_body: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    Send an email with multiple attachments using Gmail
    
    Args:
        to: Email recipient(s). Can be a single email or comma-separated list
        subject: Email subject line
        body: Plain text email body content
        attachment_paths: List of paths to files to attach
        cc: Optional carbon copy recipient(s)
        bcc: Optional blind carbon copy recipient(s)
        html_body: Optional HTML version of the email body
        ctx: MCP Context (automatically injected)
    
    Returns:
        Message confirming email was sent and the message ID
    """
    try:
        if ctx:
            ctx.info(f"Preparing to send email with multiple attachments to {to}")
            
        service = get_gmail_service()
        
        # Get user profile to use as From address
        profile = get_profile(service)
        from_email = profile.get('emailAddress', '')
        
        # Create email message
        message = MIMEMultipart('mixed')
        message['To'] = to
        message['Subject'] = subject
        message['From'] = from_email
        
        if cc:
            message['Cc'] = cc
            
        if bcc:
            message['Bcc'] = bcc
        
        # Create the message body as multipart/alternative
        msgAlternative = MIMEMultipart('alternative')
        message.attach(msgAlternative)
        
        # Attach plain text version
        msgAlternative.attach(MIMEText(body, 'plain'))
        
        # Attach HTML version if provided
        if html_body:
            msgAlternative.attach(MIMEText(html_body, 'html'))
        
        # Attach files
        attached_files = []
        missing_files = []
        
        for attachment_path in attachment_paths:
            if os.path.isfile(attachment_path):
                filename = os.path.basename(attachment_path)
                
                if ctx:
                    ctx.info(f"Attaching file: {filename}")
                    
                with open(attachment_path, 'rb') as file:
                    part = MIMEApplication(file.read(), Name=filename)
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    message.attach(part)
                attached_files.append(filename)
            else:
                missing_files.append(attachment_path)
        
        if missing_files:
            warning_msg = f"Warning: The following attachment files were not found: {', '.join(missing_files)}"
            if ctx:
                ctx.warning(warning_msg)
            
            if not attached_files:
                return f"Error: None of the specified attachment files were found. Email not sent."
        
        # Convert message to string and then to base64 URL-safe string
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Create message dict for Gmail API
        message_dict = {
            'raw': encoded_message
        }
        
        # Send the message
        if ctx:
            ctx.info("Sending email with attachments...")
            
        message_result = send_message(service, message_dict)
        
        if ctx:
            ctx.info(f"Email sent successfully with ID: {message_result['id']}")
            
        return f"Email with {len(attached_files)} attachment(s) sent successfully to {to}.\nSubject: {subject}\nAttached files: {', '.join(attached_files)}\nMessage ID: {message_result['id']}"
    
    except Exception as e:
        error_msg = f"Error sending email with attachments: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def create_email_draft(
    to: str, 
    subject: str, 
    body: str, 
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html_body: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    Create an email draft in Gmail
    
    Args:
        to: Email recipient(s). Can be a single email or comma-separated list
        subject: Email subject line
        body: Plain text email body content
        cc: Optional carbon copy recipient(s)
        bcc: Optional blind carbon copy recipient(s)
        html_body: Optional HTML version of the email body
        ctx: MCP Context (automatically injected)
    
    Returns:
        Message confirming draft was created and the draft ID
    """
    try:
        if ctx:
            ctx.info(f"Creating email draft to {to}")
            
        service = get_gmail_service()
        
        # Get user profile to use as From address
        profile = get_profile(service)
        from_email = profile.get('emailAddress', '')
        
        # Create email message
        message = MIMEMultipart('alternative')
        message['To'] = to
        message['Subject'] = subject
        message['From'] = from_email
        
        if cc:
            message['Cc'] = cc
            
        if bcc:
            message['Bcc'] = bcc
        
        # Attach plain text version
        message.attach(MIMEText(body, 'plain'))
        
        # Attach HTML version if provided
        if html_body:
            message.attach(MIMEText(html_body, 'html'))
        
        # Convert message to string and then to base64 URL-safe string
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Create message dict for Gmail API
        message_dict = {
            'raw': encoded_message
        }
        
        # Create the draft
        draft_result = create_draft(service, message_dict)
        
        if ctx:
            ctx.info(f"Draft created successfully with ID: {draft_result['id']}")
            
        return f"Draft created successfully.\nTo: {to}\nSubject: {subject}\nDraft ID: {draft_result['id']}"
    
    except Exception as e:
        error_msg = f"Error creating draft: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def update_email_draft(
    draft_id: str,
    to: Optional[str] = None, 
    subject: Optional[str] = None, 
    body: Optional[str] = None, 
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    html_body: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    Update an existing email draft with new details.
    All fields are optional; only provided fields will be updated.
    """
    try:
        if ctx:
            ctx.info(f"Attempting to update draft with ID: {draft_id}")
            
        service = get_gmail_service()
        
        # Get existing draft
        draft_data = get_draft(service, draft_id) # From utils.gmail_api
        
        if not draft_data:
            error_msg = f"Error: Draft with ID '{draft_id}' not found."
            logger.error(error_msg)
            if ctx:
                ctx.error(error_msg)
            return error_msg

        # Use existing values if new ones are not provided
        existing_message = draft_data.get('message', {})
        existing_payload = existing_message.get('payload', {})
        existing_headers = {
            header['name'].lower(): header['value'] 
            for header in existing_payload.get('headers', [])
        }

        # Determine final values for To, Subject, Cc, Bcc
        final_to = to if to is not None else existing_headers.get('to', '')
        final_subject = subject if subject is not None else existing_headers.get('subject', '')
        final_cc = cc if cc is not None else existing_headers.get('cc', None)
        final_bcc = bcc if bcc is not None else existing_headers.get('bcc', None)

        # Determine final body (plain and HTML)
        # This part needs more careful handling to preserve existing body if not overridden
        # For simplicity, this example assumes new body/html_body replaces old if provided
        # A more robust solution would parse existing parts.

        final_plain_body = body
        final_html_body = html_body

        if body is None and html_body is None: # Neither new plain nor HTML body provided
            # Attempt to extract existing body parts
            # This is a simplified extraction; real email parsing can be more complex
            parts = existing_payload.get('parts', [])
            if not parts and 'body' in existing_payload and 'data' in existing_payload['body']: # Single part, not multipart
                 # This could be plain or HTML, check mimetype
                if existing_payload.get('mimeType') == 'text/plain':
                    final_plain_body = base64.urlsafe_b64decode(existing_payload['body']['data']).decode('utf-8')
                elif existing_payload.get('mimeType') == 'text/html':
                    final_html_body = base64.urlsafe_b64decode(existing_payload['body']['data']).decode('utf-8')
            else: # Multipart
                for part in parts:
                    if final_plain_body is None and part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                        final_plain_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    if final_html_body is None and part.get('mimeType') == 'text/html' and 'data' in part.get('body', {}):
                        final_html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            
            # If still no plain body, use an empty string as a fallback to avoid errors
            if final_plain_body is None:
                final_plain_body = ""


        # Create new MIME message
        if final_html_body:
            new_mime_message = MIMEMultipart('alternative')
            if final_plain_body: # Ensure plain body is not None
                 new_mime_message.attach(MIMEText(final_plain_body, 'plain'))
            else: # if only html body is present
                 new_mime_message.attach(MIMEText('', 'plain')) # Attach empty plain part as per RFC
            new_mime_message.attach(MIMEText(final_html_body, 'html'))
        elif final_plain_body is not None: # Ensure plain body is not None
            new_mime_message = MIMEText(final_plain_body, 'plain')
        else: # Should not happen if fallback to "" is used
            error_msg = "Error: Cannot update draft with empty body. Provide plain or HTML body."
            logger.error(error_msg)
            if ctx: ctx.error(error_msg)
            return error_msg


        new_mime_message['To'] = final_to
        new_mime_message['Subject'] = final_subject
        if final_cc:
            new_mime_message['Cc'] = final_cc
        if final_bcc:
            new_mime_message['Bcc'] = final_bcc
        
        # Get user profile to use as From address (important if not set in original draft)
        profile = get_profile(service)
        from_email = profile.get('emailAddress', '')
        new_mime_message['From'] = from_email

        encoded_message = base64.urlsafe_b64encode(new_mime_message.as_bytes()).decode('utf-8')
        
        updated_message_body = {'raw': encoded_message}
        
        # Update the draft
        if ctx:
            ctx.info(f"Sending update request for draft ID: {draft_id}")
            
        updated_draft = update_draft(service, draft_id, {'message': updated_message_body}) # from utils.gmail_api
        
        if ctx:
            ctx.info(f"Draft {updated_draft['id']} updated successfully.")
            
        return f"Draft '{final_subject}' (ID: {updated_draft['id']}) updated successfully."

    except HttpError as he:
        error_detail = f"Gmail API error: {he.resp.status} - {he._get_reason()}"
        try:
            error_content = json.loads(he.content.decode())
            error_detail = error_content.get("error", {}).get("message", error_detail)
        except:
            pass # Keep original error_detail if parsing fails
        logger.error(f"API error updating draft {draft_id}: {error_detail}")
        if ctx: ctx.error(f"API Error: {error_detail}")
        return f"Error updating draft: {error_detail}"
    except Exception as e:
        error_msg = f"Unexpected error updating draft {draft_id}: {str(e)}"
        logger.exception(error_msg) # Use logger.exception to include stack trace
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def send_draft(
    draft_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Send an existing draft email
    
    Args:
        draft_id: The ID of the draft to send
        ctx: MCP Context (automatically injected)
    
    Returns:
        Message confirming draft was sent
    """
    try:
        if ctx:
            ctx.info(f"Sending draft {draft_id}")
            
        service = get_gmail_service()
        
        # Get the draft
        draft = get_draft(service, draft_id)
        if not draft:
            error_msg = f"Draft with ID {draft_id} not found"
            if ctx:
                ctx.error(error_msg)
            return error_msg
        
        # Send the draft
        result = service.users().drafts().send(
            userId='me',
            body={'id': draft_id}
        ).execute()
        
        message_id = result.get('id', 'unknown')
        
        if ctx:
            ctx.info(f"Draft sent successfully with message ID: {message_id}")
            
        return f"Draft sent successfully. Message ID: {message_id}"
    
    except Exception as e:
        error_msg = f"Error sending draft: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def list_email_drafts(
    max_results: int = 10,
    ctx: Optional[Context] = None
) -> str:
    """
    List email drafts in Gmail
    
    Args:
        max_results: Maximum number of drafts to list (default 10)
        ctx: MCP Context (automatically injected)
    
    Returns:
        A formatted list of email drafts
    """
    try:
        if ctx:
            ctx.info(f"Listing up to {max_results} email drafts")
            
        service = get_gmail_service()
        
        # List drafts
        drafts_result = list_drafts(service, max_results)
        drafts = drafts_result.get('drafts', [])
        
        if not drafts:
            return "No email drafts found."
        
        # Format results
        result = f"Found {len(drafts)} email drafts:\n\n"
        
        for i, draft in enumerate(drafts):
            # Get the draft message
            draft_message = get_message(service, draft['message']['id'], format='metadata')
            
            # Extract headers
            headers = draft_message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            recipient = next((h['value'] for h in headers if h['name'].lower() == 'to'), 'No Recipient')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown Date')
            
            result += f"{i+1}. Draft ID: {draft['id']}\n"
            result += f"   Subject: {subject}\n"
            result += f"   To: {recipient}\n"
            result += f"   Created: {date}\n"
            result += "   --------------------------------------------------\n"
        
        return result
    
    except Exception as e:
        error_msg = f"Error listing drafts: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def search_emails(
    query: str, 
    max_results: int = 10,
    ctx: Optional[Context] = None
) -> str:
    """
    Search for emails in Gmail using Gmail's search syntax
    
    Args:
        query: Gmail search query (e.g., "from:user@example.com", "subject:meeting", "is:unread")
        max_results: Maximum number of results to return (default 10)
        ctx: MCP Context (automatically injected)
    
    Returns:
        A formatted list of email results with ID, subject, sender, and date
    """
    try:
        if ctx:
            ctx.info(f"Searching emails with query: '{query}'")
            
        service = get_gmail_service()
        
        # Search for messages matching query
        messages = search_messages(service, query, max_results)
        
        if not messages:
            return f"No emails found matching query: '{query}'."
        
        # Format results
        result = f"Found {len(messages)} emails matching your query:\n\n"
        
        for i, msg_id in enumerate(messages):
            if ctx:
                ctx.report_progress(i, len(messages))
                
            msg = get_message(service, msg_id)
            
            # Extract headers
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown Date')
            
            # Format the date
            try:
                parsed_date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
                date = parsed_date.strftime("%Y-%m-%d %H:%M")
            except:
                # If date parsing fails, use the original string
                pass
            
            # Check if message has labels
            labels = msg.get('labelIds', [])
            label_str = ", ".join(labels) if labels else "None"
            
            # Check if message has attachments
            has_attachment = False
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part.get('filename'):
                        has_attachment = True
                        break
            
            result += f"{i+1}. Message ID: {msg['id']}\n"
            result += f"   Subject: {subject}\n"
            result += f"   From: {sender}\n"
            result += f"   Date: {date}\n"
            result += f"   Labels: {label_str}\n"
            result += f"   Has Attachments: {'Yes' if has_attachment else 'No'}\n"
            result += "   --------------------------------------------------\n"
        
        return result
    
    except Exception as e:
        error_msg = f"Error searching emails: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def read_email(
    message_id: str,
    include_attachments: bool = False,
    ctx: Optional[Context] = None
) -> str:
    """
    Read the content of a specific email by its ID
    
    Args:
        message_id: The Gmail message ID to read
        include_attachments: Whether to include information about attachments
        ctx: MCP Context (automatically injected)
    
    Returns:
        The full content of the email including headers and body
    """
    try:
        if ctx:
            ctx.info(f"Reading email with ID: {message_id}")
            
        service = get_gmail_service()
        
        # Get the message with full content
        msg = get_message(service, message_id, format='full')
        
        # Extract headers
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
        recipient = next((h['value'] for h in headers if h['name'].lower() == 'to'), 'Unknown Recipient')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown Date')
        cc = next((h['value'] for h in headers if h['name'].lower() == 'cc'), None)
        
        # Format date if possible
        try:
            parsed_date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
            date = parsed_date.strftime("%Y-%m-%d %H:%M")
        except:
            # If date parsing fails, use the original string
            pass
        
        # Decode subject if needed
        try:
            decoded_subject_parts = decode_header(subject)
            subject = ''.join([
                part.decode(charset or 'utf-8') if isinstance(part, bytes) else part
                for part, charset in decoded_subject_parts
            ])
        except:
            # If decoding fails, use the original string
            pass
        
        # Format headers
        result = f"Subject: {subject}\n"
        result += f"From: {sender}\n"
        result += f"To: {recipient}\n"
        if cc:
            result += f"Cc: {cc}\n"
        result += f"Date: {date}\n"
        
        # Check for labels
        labels = msg.get('labelIds', [])
        if labels:
            result += f"Labels: {', '.join(labels)}\n"
        
        result += "--------------------------------------------------\n\n"
        
        # Extract message body - recursively process all parts
        def get_body_and_attachments(payload, attachments=None):
            if attachments is None:
                attachments = []
            
            # Base case: This is a simple part with data
            if 'body' in payload and 'data' in payload['body'] and payload['body']['data']:
                mime_type = payload.get('mimeType', 'text/plain')
                part_data = payload['body']['data']
                decoded_data = base64.urlsafe_b64decode(part_data).decode('utf-8', errors='replace')
                
                return [(mime_type, decoded_data)], attachments
            
            # This part has a filename - it's an attachment
            if 'filename' in payload and payload['filename']:
                filename = payload['filename']
                mime_type = payload.get('mimeType', 'application/octet-stream')
                
                # Include attachment info if requested
                if include_attachments:
                    size = int(payload['body'].get('size', 0))
                    size_str = f"{size} bytes"
                    if size > 1024:
                        size_str = f"{size/1024:.1f} KB"
                    if size > 1024*1024:
                        size_str = f"{size/1024/1024:.1f} MB"
                        
                    attachments.append({
                        'filename': filename,
                        'mimeType': mime_type,
                        'size': size_str
                    })
                
                return [], attachments
            
            # Recursive case: This is a multipart message
            if 'parts' in payload:
                all_parts = []
                
                for part in payload['parts']:
                    part_bodies, updated_attachments = get_body_and_attachments(part, attachments)
                    all_parts.extend(part_bodies)
                    attachments = updated_attachments
                
                return all_parts, attachments
            
            return [], attachments
        
        parts, attachments = get_body_and_attachments(msg['payload'])
        
        # Prefer plain text if available, otherwise use HTML
        plain_text_parts = [content for mime_type, content in parts if mime_type == 'text/plain']
        html_parts = [content for mime_type, content in parts if mime_type == 'text/html']
        
        if plain_text_parts:
            body = "\n".join(plain_text_parts)
        elif html_parts:
            # Very simple HTML to text conversion
            body = html_parts[0]
            body = re.sub(r'<br\s*/?>|</(p|div|h\d)>', '\n', body)
            body = re.sub(r'<.*?>', '', body)
            body = re.sub(r'&nbsp;', ' ', body)
            body = re.sub(r'&lt;', '<', body)
            body = re.sub(r'&gt;', '>', body)
            body = re.sub(r'&amp;', '&', body)
        else:
            body = "Unable to extract email body content. The email might be empty or contain only non-text attachments."
        
        result += body
        
        # Add attachment information if requested
        if include_attachments and attachments:
            result += "\n\n--------------------------------------------------\n"
            result += f"Attachments ({len(attachments)}):\n"
            
            for i, attachment in enumerate(attachments):
                result += f"{i+1}. {attachment['filename']} ({attachment['mimeType']}, {attachment['size']})\n"
        
        return result
    
    except Exception as e:
        error_msg = f"Error reading email: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def get_unread_emails(
    max_results: int = 5,
    ctx: Optional[Context] = None
) -> str:
    """
    Get a list of unread emails
    
    Args:
        max_results: Maximum number of results to return (default 5)
        ctx: MCP Context (automatically injected)
    
    Returns:
        A formatted list of unread emails
    """
    if ctx:
        ctx.info(f"Getting up to {max_results} unread emails")
        
    return await search_emails("is:unread", max_results, ctx)

@mcp.tool()
async def get_important_emails(
    max_results: int = 5,
    ctx: Optional[Context] = None
) -> str:
    """
    Get a list of emails marked as important
    
    Args:
        max_results: Maximum number of results to return (default 5)
        ctx: MCP Context (automatically injected)
    
    Returns:
        A formatted list of important emails
    """
    if ctx:
        ctx.info(f"Getting up to {max_results} important emails")
        
    return await search_emails("is:important", max_results, ctx)

@mcp.tool()
async def get_emails_with_attachments(
    max_results: int = 5,
    query: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    Get a list of emails with attachments
    
    Args:
        max_results: Maximum number of results to return (default 5)
        query: Optional additional search query
        ctx: MCP Context (automatically injected)
    
    Returns:
        A formatted list of emails with attachments
    """
    if ctx:
        ctx.info(f"Getting up to {max_results} emails with attachments")
        
    search_query = "has:attachment"
    if query:
        search_query += f" {query}"
        
    return await search_emails(search_query, max_results, ctx)

@mcp.tool()
async def get_recent_emails(
    max_results: int = 5,
    days: int = 7,
    ctx: Optional[Context] = None
) -> str:
    """
    Get a list of recent emails
    
    Args:
        max_results: Maximum number of results to return (default 5)
        days: Number of days to look back (default 7)
        ctx: MCP Context (automatically injected)
    
    Returns:
        A formatted list of recent emails
    """
    if ctx:
        ctx.info(f"Getting up to {max_results} emails from the last {days} days")
        
    # Calculate date for query
    date = (datetime.now() - timedelta(days=days)).strftime("%Y/%m/%d")
    search_query = f"after:{date}"
        
    return await search_emails(search_query, max_results, ctx)

@mcp.tool()
async def get_email_labels(
    ctx: Optional[Context] = None
) -> str:
    """
    Get all Gmail labels (folders)
    
    Args:
        ctx: MCP Context (automatically injected)
    
    Returns:
        A formatted list of all Gmail labels
    """
    try:
        if ctx:
            ctx.info("Getting Gmail labels")
            
        service = get_gmail_service()
        
        labels = get_labels(service)
        
        if not labels:
            return "No labels found in this Gmail account."
        
        # Separate system and user labels
        system_labels = [label for label in labels if label.get('type') == 'system']
        user_labels = [label for label in labels if label.get('type') == 'user']
        
        result = "Gmail Labels:\n\n"
        
        if system_labels:
            result += "System Labels:\n"
            for label in system_labels:
                result += f"- {label['name']} (ID: {label['id']})\n"
        
        if user_labels:
            result += "\nUser Labels:\n"
            for label in user_labels:
                result += f"- {label['name']} (ID: {label['id']})\n"
        
        return result
    
    except Exception as e:
        error_msg = f"Error getting labels: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def create_email_label(
    name: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Create a new Gmail label
    
    Args:
        name: The name of the label to create
        ctx: MCP Context (automatically injected)
    
    Returns:
        Confirmation message
    """
    try:
        if ctx:
            ctx.info(f"Creating new label: {name}")
            
        service = get_gmail_service()
        
        # Check if label already exists
        existing_labels = get_labels(service)
        for label in existing_labels:
            if label['name'].lower() == name.lower():
                return f"Label '{name}' already exists with ID: {label['id']}"
        
        # Create the label
        new_label = create_label(service, name)
        
        return f"Label '{name}' created successfully with ID: {new_label['id']}"
    
    except Exception as e:
        error_msg = f"Error creating label: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def delete_email_label(
    name: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Delete a Gmail label
    
    Args:
        name: The name of the label to delete
        ctx: MCP Context (automatically injected)
    
    Returns:
        Confirmation message
    """
    try:
        if ctx:
            ctx.info(f"Deleting label: {name}")
            
        service = get_gmail_service()
        
        # Find label ID from name
        labels = get_labels(service)
        label_id = None
        
        for label in labels:
            if label['name'].lower() == name.lower():
                label_id = label['id']
                break
        
        if not label_id:
            return f"Label '{name}' not found. Please check the label name."
        
        # Check if it's a system label
        for label in labels:
            if label['id'] == label_id and label.get('type') == 'system':
                return f"Cannot delete system label '{name}'."
        
        # Delete the label
        delete_label(service, label_id)
        
        return f"Label '{name}' deleted successfully."
    
    except Exception as e:
        error_msg = f"Error deleting label: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def label_email(
    message_id: str, 
    label_name: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Apply a label to an email
    
    Args:
        message_id: The Gmail message ID
        label_name: The name of the label to apply
        ctx: MCP Context (automatically injected)
    
    Returns:
        Confirmation message
    """
    try:
        if ctx:
            ctx.info(f"Applying label '{label_name}' to message {message_id}")
            
        service = get_gmail_service()
        
        # Get message to verify it exists
        try:
            msg = get_message(service, message_id)
        except Exception:
            return f"Message with ID {message_id} not found."
        
        # Get label ID from name
        labels = get_labels(service)
        label_id = None
        
        for label in labels:
            if label['name'].lower() == label_name.lower():
                label_id = label['id']
                break
        
        if not label_id:
            # Create the label if it doesn't exist
            if ctx:
                ctx.info(f"Label '{label_name}' not found. Creating new label.")
            
            new_label = create_label(service, label_name)
            label_id = new_label['id']
        
        # Apply the label
        apply_label(service, message_id, label_id)
        
        return f"Label '{label_name}' applied to message {message_id}"
    
    except Exception as e:
        error_msg = f"Error applying label: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def remove_email_label(
    message_id: str, 
    label_name: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Remove a label from an email
    
    Args:
        message_id: The Gmail message ID
        label_name: The name of the label to remove
        ctx: MCP Context (automatically injected)
    
    Returns:
        Confirmation message
    """
    try:
        if ctx:
            ctx.info(f"Removing label '{label_name}' from message {message_id}")
            
        service = get_gmail_service()
        
        # Get message to verify it exists
        try:
            msg = get_message(service, message_id)
        except Exception:
            return f"Message with ID {message_id} not found."
        
        # Get label ID from name
        labels = get_labels(service)
        label_id = None
        
        for label in labels:
            if label['name'].lower() == label_name.lower():
                label_id = label['id']
                break
        
        if not label_id:
            return f"Label '{label_name}' not found. Please check the label name."
        
        # Check if the message has this label
        if 'labelIds' not in msg or label_id not in msg['labelIds']:
            return f"Message {message_id} does not have label '{label_name}'."
        
        # Remove the label
        remove_label(service, message_id, label_id)
        
        return f"Label '{label_name}' removed from message {message_id}"
    
    except Exception as e:
        error_msg = f"Error removing label: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def mark_as_read(
    message_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Mark an email as read
    
    Args:
        message_id: The Gmail message ID
        ctx: MCP Context (automatically injected)
    
    Returns:
        Confirmation message
    """
    try:
        if ctx:
            ctx.info(f"Marking message {message_id} as read")
            
        service = get_gmail_service()
        
        # Get message to verify it exists
        try:
            msg = get_message(service, message_id)
        except Exception:
            return f"Message with ID {message_id} not found."
        
        # Check if message is already read
        if 'labelIds' in msg and 'UNREAD' not in msg['labelIds']:
            return f"Message {message_id} is already marked as read."
        
        # Remove UNREAD label
        modify_message(service, message_id, {'removeLabelIds': ['UNREAD']})
        
        return f"Message {message_id} marked as read"
    
    except Exception as e:
        error_msg = f"Error marking message as read: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def mark_as_unread(
    message_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Mark an email as unread
    
    Args:
        message_id: The Gmail message ID
        ctx: MCP Context (automatically injected)
    
    Returns:
        Confirmation message
    """
    try:
        if ctx:
            ctx.info(f"Marking message {message_id} as unread")
            
        service = get_gmail_service()
        
        # Get message to verify it exists
        try:
            msg = get_message(service, message_id)
        except Exception:
            return f"Message with ID {message_id} not found."
        
        # Check if message is already unread
        if 'labelIds' in msg and 'UNREAD' in msg['labelIds']:
            return f"Message {message_id} is already marked as unread."
        
        # Add UNREAD label
        modify_message(service, message_id, {'addLabelIds': ['UNREAD']})
        
        return f"Message {message_id} marked as unread"
    
    except Exception as e:
        error_msg = f"Error marking message as unread: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def delete_email(
    message_id: str,
    ctx: Optional[Context] = None
) -> str:
    """
    Move an email to trash
    
    Args:
        message_id: The Gmail message ID
        ctx: MCP Context (automatically injected)
    
    Returns:
        Confirmation message
    """
    try:
        if ctx:
            ctx.info(f"Moving message {message_id} to trash")
            
        service = get_gmail_service()
        
        # Get message to verify it exists
        try:
            msg = get_message(service, message_id)
        except Exception:
            return f"Message with ID {message_id} not found."
            
        delete_message(service, message_id)
        
        return f"Message {message_id} moved to trash."
    
    except Exception as e:
        error_msg = f"Error deleting message: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def batch_apply_label(
    query: str,
    label_name: str,
    max_messages: int = 50,
    ctx: Optional[Context] = None
) -> str:
    """
    Apply a label to multiple emails matching a search query
    
    Args:
        query: Gmail search query
        label_name: The name of the label to apply
        max_messages: Maximum number of messages to process (default 50)
        ctx: MCP Context (automatically injected)
    
    Returns:
        Confirmation message
    """
    try:
        if ctx:
            ctx.info(f"Applying label '{label_name}' to messages matching query: '{query}'")
            
        service = get_gmail_service()
        
        # Search for messages
        message_ids = search_messages(service, query, max_messages)
        
        if not message_ids:
            return f"No messages found matching query: '{query}'."
        
        # Get label ID from name
        labels = get_labels(service)
        label_id = None
        
        for label in labels:
            if label['name'].lower() == label_name.lower():
                label_id = label['id']
                break
        
        if not label_id:
            # Create the label if it doesn't exist
            if ctx:
                ctx.info(f"Label '{label_name}' not found. Creating new label.")
            
            new_label = create_label(service, label_name)
            label_id = new_label['id']
        
        # Apply the label to all messages
        total = len(message_ids)
        success_count = 0
        
        for i, msg_id in enumerate(message_ids):
            if ctx:
                ctx.report_progress(i, total)
                
            try:
                apply_label(service, msg_id, label_id)
                success_count += 1
                # Small sleep to avoid rate limiting
                time.sleep(0.1)
            except Exception as e:
                logger.warning(f"Error applying label to message {msg_id}: {str(e)}")
        
        return f"Label '{label_name}' applied to {success_count} out of {total} messages that matched your query."
    
    except Exception as e:
        error_msg = f"Error batch applying label: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def batch_delete_emails(
    query: str,
    max_messages: int = 50,
    ctx: Optional[Context] = None
) -> str:
    """
    Move multiple emails matching a search query to trash
    
    Args:
        query: Gmail search query
        max_messages: Maximum number of messages to process (default 50)
        ctx: MCP Context (automatically injected)
    
    Returns:
        Confirmation message
    """
    try:
        if ctx:
            ctx.info(f"Moving messages matching query '{query}' to trash")
            
        service = get_gmail_service()
        
        # Search for messages
        message_ids = search_messages(service, query, max_messages)
        
        if not message_ids:
            return f"No messages found matching query: '{query}'."
        
        # Delete all messages
        total = len(message_ids)
        success_count = 0
        
        for i, msg_id in enumerate(message_ids):
            if ctx:
                ctx.report_progress(i, total)
                
            try:
                delete_message(service, msg_id)
                success_count += 1
                # Small sleep to avoid rate limiting
                time.sleep(0.1)
            except Exception as e:
                logger.warning(f"Error deleting message {msg_id}: {str(e)}")
        
        return f"Moved {success_count} out of {total} messages that matched your query to trash."
    
    except Exception as e:
        error_msg = f"Error batch deleting messages: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def get_email_profile(
    ctx: Optional[Context] = None
) -> str:
    """
    Get the user's Gmail profile information
    
    Args:
        ctx: MCP Context (automatically injected)
    
    Returns:
        User's Gmail profile information
    """
    try:
        if ctx:
            ctx.info("Getting Gmail profile information")
            
        service = get_gmail_service()
        
        profile = get_profile(service)
        
        if not profile:
            return "Could not retrieve Gmail profile information."
        
        result = "Gmail Profile Information:\n\n"
        result += f"Email Address: {profile.get('emailAddress', 'Unknown')}\n"
        
        # Get label usage information
        total_space = int(profile.get('quotaBytesTotal', 0))
        used_space = int(profile.get('quotaBytesUsed', 0))
        
        # Convert to human-readable format
        def format_size(size_bytes):
            if size_bytes < 1024:
                return f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.2f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.2f} MB"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
        
        if total_space > 0:
            result += f"Storage Used: {format_size(used_space)} of {format_size(total_space)}\n"
            result += f"Storage Usage: {(used_space / total_space) * 100:.2f}%\n"
        
        # Add information about labels
        labels = get_labels(service)
        num_labels = len(labels)
        num_user_labels = len([l for l in labels if l.get('type') == 'user'])
        
        result += f"Total Labels: {num_labels} ({num_user_labels} user labels)\n"
        
        # Add message count information
        # This requires searching for all messages, which can be slow for large inboxes
        # So we'll just do a basic check for total message count
        try:
            all_messages = search_messages(service, "", max_results=1)
            if 'resultSizeEstimate' in all_messages:
                result += f"Estimated Message Count: {all_messages['resultSizeEstimate']}\n"
        except:
            pass
        
        return result
    
    except Exception as e:
        error_msg = f"Error getting Gmail profile: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

@mcp.tool()
async def summarize_recent_emails(
    max_emails: int = 10,
    days: int = 3,
    query: Optional[str] = None,
    ctx: Optional[Context] = None
) -> str:
    """
    Summarize recent emails in a concise format
    
    Args:
        max_emails: Maximum number of emails to summarize (default 10)
        days: Number of days to look back (default 3)
        query: Optional additional search query
        ctx: MCP Context (automatically injected)
    
    Returns:
        A summary of recent emails
    """
    try:
        if ctx:
            ctx.info(f"Summarizing recent emails from the last {days} days")
            
        service = get_gmail_service()
        
        # Calculate date for query
        date = (datetime.now() - timedelta(days=days)).strftime("%Y/%m/%d")
        search_query = f"after:{date}"
        
        if query:
            search_query += f" {query}"
        
        # Search for messages
        message_ids = search_messages(service, search_query, max_emails)
        
        if not message_ids:
            return f"No emails found in the last {days} days" + (f" matching query: '{query}'" if query else ".")
        
        # Get details for each message
        summary = f"Summary of {len(message_ids)} recent emails"
        if query:
            summary += f" matching '{query}'"
        summary += f" from the last {days} days:\n\n"
        
        for i, msg_id in enumerate(message_ids):
            if ctx:
                ctx.report_progress(i, len(message_ids))
                
            msg = get_message(service, msg_id)
            
            # Extract headers
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown Date')
            
            # Format the date
            try:
                parsed_date = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S %z")
                date = parsed_date.strftime("%Y-%m-%d %H:%M")
            except:
                # If date parsing fails, use the original string
                pass
            
            # Extract sender name if available
            sender_name = sender
            match = re.search(r'"?([^"<]+)"?\s*(?:<[^>]+>)?', sender)
            if match:
                sender_name = match.group(1).strip()
            
            # Check labels
            labels = msg.get('labelIds', [])
            is_unread = 'UNREAD' in labels
            is_important = 'IMPORTANT' in labels
            
            # Format summary line
            summary += f"{i+1}. {subject}\n"
            summary += f"   From: {sender_name} | {date}"
            
            if is_unread:
                summary += " | UNREAD"
            if is_important:
                summary += " | IMPORTANT"
                
            summary += f"\n   ID: {msg_id}\n\n"
        
        return summary
    
    except Exception as e:
        error_msg = f"Error summarizing emails: {str(e)}"
        logger.error(error_msg)
        if ctx:
            ctx.error(error_msg)
        return error_msg

# Run the server when the script is executed directly
if __name__ == "__main__":
    import sys
    
    # Check if we should run with SSE instead of stdio
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        mount_path = "/sse"
        if len(sys.argv) > 2:
            mount_path = sys.argv[2]
        print(f"Starting Gmail MCP Server with SSE transport at {mount_path}")
        mcp.run(transport='sse', mount_path=mount_path)
    else:
        # Default to stdio transport
        print("Starting Gmail MCP Server with stdio transport")
        mcp.run()
