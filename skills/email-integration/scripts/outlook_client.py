#!/usr/bin/env python3
"""
Outlook/Microsoft Graph API client for email operations.
Requires: msal, requests
Install: pip install msal requests
"""

import os
import json
import msal
import requests
from typing import List, Dict, Optional

class OutlookClient:
    def __init__(self, client_id, client_secret=None, tenant_id='common', token_cache_path='outlook_token_cache.json'):
        """
        Initialize Outlook client with Microsoft Graph API.
        
        Args:
            client_id: Azure AD application (client) ID
            client_secret: Client secret (optional, for confidential clients)
            tenant_id: Azure AD tenant ID (default: 'common' for multi-tenant)
            token_cache_path: Path to store token cache
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.token_cache_path = token_cache_path
        self.authority = f'https://login.microsoftonline.com/{tenant_id}'
        self.scopes = ['https://graph.microsoft.com/Mail.ReadWrite', 
                      'https://graph.microsoft.com/Mail.Send']
        self.graph_endpoint = 'https://graph.microsoft.com/v1.0'
        self.access_token = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Microsoft Graph API using MSAL."""
        cache = msal.SerializableTokenCache()
        
        # Load cache if exists
        if os.path.exists(self.token_cache_path):
            with open(self.token_cache_path, 'r') as f:
                cache.deserialize(f.read())
        
        if self.client_secret:
            # Confidential client (service/daemon app)
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret,
                token_cache=cache
            )
        else:
            # Public client (interactive auth)
            app = msal.PublicClientApplication(
                self.client_id,
                authority=self.authority,
                token_cache=cache
            )
        
        # Try to get token from cache
        accounts = app.get_accounts()
        result = None
        
        if accounts:
            result = app.acquire_token_silent(self.scopes, account=accounts[0])
        
        # If no cached token, do interactive auth
        if not result:
            if self.client_secret:
                # Service/daemon flow
                result = app.acquire_token_for_client(scopes=self.scopes)
            else:
                # Interactive flow
                result = app.acquire_token_interactive(scopes=self.scopes)
        
        # Save cache
        if cache.has_state_changed:
            with open(self.token_cache_path, 'w') as f:
                f.write(cache.serialize())
        
        if 'access_token' in result:
            self.access_token = result['access_token']
        else:
            raise Exception(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make authenticated request to Microsoft Graph API."""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']
        
        url = f"{self.graph_endpoint}{endpoint}"
        response = requests.request(method, url, headers=headers, **kwargs)
        
        if response.status_code == 401:
            # Token expired, re-authenticate
            self._authenticate()
            headers['Authorization'] = f'Bearer {self.access_token}'
            response = requests.request(method, url, headers=headers, **kwargs)
        
        if response.status_code >= 400:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
        
        return response.json() if response.content else {}
    
    def list_messages(self, folder='inbox', filter_query=None, max_results=10):
        """
        List messages from a folder.
        
        Args:
            folder: Folder name ('inbox', 'sentitems', 'drafts', etc.)
            filter_query: OData filter (e.g., "isRead eq false", "from/emailAddress/address eq 'user@example.com'")
            max_results: Maximum number of messages to return
        
        Returns:
            List of message objects
        """
        endpoint = f'/me/mailFolders/{folder}/messages'
        params = {
            '$top': max_results,
            '$orderby': 'receivedDateTime desc'
        }
        
        if filter_query:
            params['$filter'] = filter_query
        
        result = self._make_request('GET', endpoint, params=params)
        return result.get('value', [])
    
    def get_message(self, message_id):
        """Get full message details by ID."""
        endpoint = f'/me/messages/{message_id}'
        return self._make_request('GET', endpoint)
    
    def send_message(self, to, subject, body, cc=None, bcc=None, attachments=None, body_type='Text'):
        """
        Send an email message.
        
        Args:
            to: Recipient email address(es) (string or list)
            subject: Email subject
            body: Email body
            cc: CC recipients (string or list, optional)
            bcc: BCC recipients (string or list, optional)
            attachments: List of file paths to attach (optional)
            body_type: 'Text' or 'HTML'
        
        Returns:
            Response from send API
        """
        # Format recipients
        def format_recipients(emails):
            if isinstance(emails, str):
                emails = [emails]
            return [{'emailAddress': {'address': email}} for email in emails]
        
        message = {
            'subject': subject,
            'body': {
                'contentType': body_type,
                'content': body
            },
            'toRecipients': format_recipients(to)
        }
        
        if cc:
            message['ccRecipients'] = format_recipients(cc)
        if bcc:
            message['bccRecipients'] = format_recipients(bcc)
        
        # Handle attachments
        if attachments:
            message['attachments'] = []
            for file_path in attachments:
                with open(file_path, 'rb') as f:
                    import base64
                    content = base64.b64encode(f.read()).decode()
                    message['attachments'].append({
                        '@odata.type': '#microsoft.graph.fileAttachment',
                        'name': os.path.basename(file_path),
                        'contentBytes': content
                    })
        
        endpoint = '/me/sendMail'
        body = {'message': message, 'saveToSentItems': 'true'}
        
        return self._make_request('POST', endpoint, json=body)
    
    def mark_as_read(self, message_ids):
        """Mark message(s) as read."""
        if isinstance(message_ids, str):
            message_ids = [message_ids]
        
        for msg_id in message_ids:
            endpoint = f'/me/messages/{msg_id}'
            self._make_request('PATCH', endpoint, json={'isRead': True})
        
        return True
    
    def mark_as_unread(self, message_ids):
        """Mark message(s) as unread."""
        if isinstance(message_ids, str):
            message_ids = [message_ids]
        
        for msg_id in message_ids:
            endpoint = f'/me/messages/{msg_id}'
            self._make_request('PATCH', endpoint, json={'isRead': False})
        
        return True
    
    def archive(self, message_ids, archive_folder='archive'):
        """Move message(s) to archive folder."""
        if isinstance(message_ids, str):
            message_ids = [message_ids]
        
        for msg_id in message_ids:
            endpoint = f'/me/messages/{msg_id}/move'
            # Try to get archive folder ID
            folders = self._make_request('GET', '/me/mailFolders')
            archive_id = None
            
            for folder in folders.get('value', []):
                if folder['displayName'].lower() == archive_folder.lower():
                    archive_id = folder['id']
                    break
            
            if not archive_id:
                raise Exception(f"Archive folder '{archive_folder}' not found")
            
            self._make_request('POST', endpoint, json={'destinationId': archive_id})
        
        return True
    
    def delete(self, message_ids):
        """Move message(s) to deleted items."""
        if isinstance(message_ids, str):
            message_ids = [message_ids]
        
        for msg_id in message_ids:
            endpoint = f'/me/messages/{msg_id}'
            self._make_request('DELETE', endpoint)
        
        return True
    
    def search(self, query, max_results=50):
        """
        Search emails using Microsoft Graph search.
        
        Args:
            query: Search query string
            max_results: Maximum number of results
        
        Examples:
            'subject:meeting'
            'from:boss@company.com'
            'hasAttachments:true received>=2024-01-01'
        """
        endpoint = '/me/messages'
        params = {
            '$search': f'"{query}"',
            '$top': max_results,
            '$orderby': 'receivedDateTime desc'
        }
        
        result = self._make_request('GET', endpoint, params=params)
        return result.get('value', [])
    
    def list_folders(self):
        """List all mail folders."""
        endpoint = '/me/mailFolders'
        result = self._make_request('GET', endpoint)
        return result.get('value', [])


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python outlook_client.py <client_id> [client_secret]")
        sys.exit(1)
    
    client_id = sys.argv[1]
    client_secret = sys.argv[2] if len(sys.argv) > 2 else None
    
    client = OutlookClient(client_id, client_secret)
    
    # List unread messages
    unread = client.list_messages(filter_query="isRead eq false", max_results=5)
    print(f"Found {len(unread)} unread messages")
    
    for msg in unread:
        print(f"\nFrom: {msg.get('from', {}).get('emailAddress', {}).get('address', 'Unknown')}")
        print(f"Subject: {msg.get('subject', 'No subject')}")
        print(f"Preview: {msg.get('bodyPreview', '')[:100]}...")
