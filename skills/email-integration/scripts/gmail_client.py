#!/usr/bin/env python3
"""
Gmail API client for email operations.
Requires: google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client
Install: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import os
import base64
import pickle
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailClient:
    def __init__(self, credentials_path='credentials.json', token_path='token.pickle'):
        """Initialize Gmail client with OAuth credentials."""
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds = None
        
        # Check if token exists
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def list_messages(self, query='', max_results=10, label_ids=None):
        """
        List messages matching query.
        
        Args:
            query: Gmail search query (e.g., 'is:unread', 'from:user@example.com')
            max_results: Maximum number of messages to return
            label_ids: List of label IDs to filter by (e.g., ['INBOX', 'UNREAD'])
        
        Returns:
            List of message objects with id, threadId, and snippet
        """
        try:
            params = {
                'userId': 'me',
                'maxResults': max_results,
                'q': query
            }
            
            if label_ids:
                params['labelIds'] = label_ids
            
            results = self.service.users().messages().list(**params).execute()
            messages = results.get('messages', [])
            
            # Get full message details
            detailed_messages = []
            for msg in messages:
                full_msg = self.get_message(msg['id'])
                detailed_messages.append(full_msg)
            
            return detailed_messages
        except Exception as e:
            raise Exception(f"Error listing messages: {str(e)}")
    
    def get_message(self, message_id):
        """Get full message details by ID."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Parse headers
            headers = {}
            for header in message['payload']['headers']:
                headers[header['name'].lower()] = header['value']
            
            # Get body
            body = self._get_body(message['payload'])
            
            return {
                'id': message['id'],
                'threadId': message['threadId'],
                'labelIds': message.get('labelIds', []),
                'snippet': message.get('snippet', ''),
                'from': headers.get('from', ''),
                'to': headers.get('to', ''),
                'subject': headers.get('subject', ''),
                'date': headers.get('date', ''),
                'body': body
            }
        except Exception as e:
            raise Exception(f"Error getting message: {str(e)}")
    
    def _get_body(self, payload):
        """Extract email body from payload."""
        body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def send_message(self, to, subject, body, cc=None, bcc=None, attachments=None):
        """
        Send an email message.
        
        Args:
            to: Recipient email address(es) (string or list)
            subject: Email subject
            body: Email body (plain text)
            cc: CC recipients (string or list, optional)
            bcc: BCC recipients (string or list, optional)
            attachments: List of file paths to attach (optional)
        
        Returns:
            Sent message object
        """
        try:
            message = MIMEMultipart()
            message['to'] = to if isinstance(to, str) else ', '.join(to)
            message['subject'] = subject
            
            if cc:
                message['cc'] = cc if isinstance(cc, str) else ', '.join(cc)
            if bcc:
                message['bcc'] = bcc if isinstance(bcc, str) else ', '.join(bcc)
            
            # Attach body
            message.attach(MIMEText(body, 'plain'))
            
            # Attach files
            if attachments:
                for file_path in attachments:
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={os.path.basename(file_path)}'
                        )
                        message.attach(part)
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            body = {'raw': raw}
            
            sent_message = self.service.users().messages().send(
                userId='me',
                body=body
            ).execute()
            
            return sent_message
        except Exception as e:
            raise Exception(f"Error sending message: {str(e)}")
    
    def mark_as_read(self, message_ids):
        """Mark message(s) as read."""
        if isinstance(message_ids, str):
            message_ids = [message_ids]
        
        try:
            self.service.users().messages().batchModify(
                userId='me',
                body={
                    'ids': message_ids,
                    'removeLabelIds': ['UNREAD']
                }
            ).execute()
            return True
        except Exception as e:
            raise Exception(f"Error marking as read: {str(e)}")
    
    def mark_as_unread(self, message_ids):
        """Mark message(s) as unread."""
        if isinstance(message_ids, str):
            message_ids = [message_ids]
        
        try:
            self.service.users().messages().batchModify(
                userId='me',
                body={
                    'ids': message_ids,
                    'addLabelIds': ['UNREAD']
                }
            ).execute()
            return True
        except Exception as e:
            raise Exception(f"Error marking as unread: {str(e)}")
    
    def archive(self, message_ids):
        """Archive message(s) by removing INBOX label."""
        if isinstance(message_ids, str):
            message_ids = [message_ids]
        
        try:
            self.service.users().messages().batchModify(
                userId='me',
                body={
                    'ids': message_ids,
                    'removeLabelIds': ['INBOX']
                }
            ).execute()
            return True
        except Exception as e:
            raise Exception(f"Error archiving: {str(e)}")
    
    def delete(self, message_ids):
        """Move message(s) to trash."""
        if isinstance(message_ids, str):
            message_ids = [message_ids]
        
        try:
            for msg_id in message_ids:
                self.service.users().messages().trash(
                    userId='me',
                    id=msg_id
                ).execute()
            return True
        except Exception as e:
            raise Exception(f"Error deleting: {str(e)}")
    
    def search(self, query, max_results=50):
        """
        Search emails with Gmail query syntax.
        
        Examples:
            'subject:meeting'
            'from:boss@company.com'
            'has:attachment after:2024/01/01'
            'is:unread label:important'
        """
        return self.list_messages(query=query, max_results=max_results)


if __name__ == '__main__':
    # Example usage
    client = GmailClient()
    
    # List unread messages
    unread = client.list_messages(query='is:unread', max_results=5)
    print(f"Found {len(unread)} unread messages")
    
    for msg in unread:
        print(f"\nFrom: {msg['from']}")
        print(f"Subject: {msg['subject']}")
        print(f"Snippet: {msg['snippet']}")
