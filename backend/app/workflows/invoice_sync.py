"""
Invoice Sync Workflow - Extract invoices from Gmail and save to Google Drive
"""
from app.workflows.base import WorkflowBase
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import os
import pickle
import base64
import io
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class InvoiceSyncWorkflow(WorkflowBase):
    """
    Syncs invoices/receipts from Gmail to Google Drive
    """
    
    # Gmail and Drive API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    def __init__(self):
        super().__init__()
        self.creds = None
        self.gmail_service = None
        self.drive_service = None
    
    def authenticate(self):
        """
        Authenticate with Google APIs using OAuth2
        """
        try:
            token_path = Path('token.pickle')
            creds_path = Path('credentials.json')
            
            # Load saved credentials
            if token_path.exists():
                with open(token_path, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # Refresh or get new credentials
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.log_info("Refreshing credentials")
                    self.creds.refresh(Request())
                else:
                    if not creds_path.exists():
                        raise FileNotFoundError(
                            "credentials.json not found. "
                            "Download it from Google Cloud Console."
                        )
                    
                    self.log_info("Starting OAuth2 flow")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(creds_path), 
                        self.SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_path, 'wb') as token:
                    pickle.dump(self.creds, token)
                self.log_info("Credentials saved")
            
            # Build services
            self.gmail_service = build('gmail', 'v1', credentials=self.creds)
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            
            self.log_info("Google APIs authenticated successfully")
            return True
            
        except Exception as e:
            self.log_error(f"Authentication failed: {str(e)}")
            raise
    
    def search_gmail(self, query, max_results=10):
        """
        Search Gmail for messages matching query
        """
        try:
            self.log_info(f"Searching Gmail with query: {query}")
            
            results = self.gmail_service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            self.log_info(f"Found {len(messages)} messages")
            
            return messages
            
        except Exception as e:
            self.log_error(f"Gmail search failed: {str(e)}")
            raise
    
    def get_message_details(self, message_id):
        """
        Get full message details including attachments
        """
        try:
            message = self.gmail_service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            return message
            
        except Exception as e:
            self.log_error(f"Failed to get message {message_id}: {str(e)}")
            return None
    
    def extract_attachments(self, message):
        """
        Extract attachments from a message
        Returns list of (filename, data) tuples
        """
        attachments = []
        
        if 'parts' not in message['payload']:
            return attachments
        
        for part in message['payload']['parts']:
            if part.get('filename'):
                filename = part['filename']
                
                # Only process PDF and image attachments
                if not any(filename.lower().endswith(ext) 
                          for ext in ['.pdf', '.png', '.jpg', '.jpeg']):
                    continue
                
                if 'attachmentId' in part['body']:
                    attachment_id = part['body']['attachmentId']
                    
                    # Get attachment data
                    attachment = self.gmail_service.users().messages().attachments().get(
                        userId='me',
                        messageId=message['id'],
                        id=attachment_id
                    ).execute()
                    
                    data = base64.urlsafe_b64decode(attachment['data'])
                    attachments.append((filename, data))
                    
                    self.log_info(f"Extracted attachment: {filename}")
        
        return attachments
    
    def create_drive_folder(self, folder_name, parent_id=None):
        """
        Create folder in Google Drive (if doesn't exist)
        Returns folder ID
        """
        try:
            # Check if folder exists
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                folder_id = folders[0]['id']
                self.log_info(f"Folder '{folder_name}' already exists: {folder_id}")
                return folder_id
            
            # Create folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = self.drive_service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            self.log_info(f"Created folder '{folder_name}': {folder_id}")
            
            return folder_id
            
        except Exception as e:
            self.log_error(f"Failed to create folder: {str(e)}")
            raise
    
    def upload_to_drive(self, filename, data, folder_id):
        """
        Upload file to Google Drive
        """
        try:
            # Create file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            # Save data temporarily
            import tempfile

            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(data)
            temp_file.close()

            temp_path = Path(temp_file.name)
            temp_path.parent.mkdir(exist_ok=True)
            
            with open(temp_path, 'wb') as f:
                f.write(data)
            
            # Upload
            media = MediaFileUpload(str(temp_path), resumable=True)
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            # Clean up
            temp_path.unlink()
            
            file_id = file.get('id')
            link = file.get('webViewLink')
            
            self.log_info(f"Uploaded '{filename}' to Drive: {file_id}")
            
            return file_id, link
            
        except Exception as e:
            self.log_error(f"Failed to upload {filename}: {str(e)}")
            return None, None
    
    def execute(self, config):
        """
        Execute invoice sync workflow
        
        Expected config:
        {
            'gmail_filter': 'invoice OR receipt OR bill',  # Gmail search query
            'drive_folder': 'Invoices',                    # Base folder name
            'organize_by_date': True,                      # Create YYYY/MM subfolders
            'max_emails': 10                               # Max emails to process
        }
        """
        try:
            self.validate_config(config, ['gmail_filter', 'drive_folder'])
            
            # Get parameters
            gmail_filter = config['gmail_filter']
            base_folder_name = config['drive_folder']
            organize_by_date = config.get('organize_by_date', True)
            max_emails = config.get('max_emails', 10)
            
            # Authenticate
            self.authenticate()
            
            # Create base folder
            base_folder_id = self.create_drive_folder(base_folder_name)
            
            # Create date-based subfolder if needed
            if organize_by_date:
                now = datetime.now()
                year_folder_id = self.create_drive_folder(
                    str(now.year), 
                    base_folder_id
                )
                month_folder_id = self.create_drive_folder(
                    now.strftime('%m - %B'),
                    year_folder_id
                )
                target_folder_id = month_folder_id
            else:
                target_folder_id = base_folder_id
            
            # Search Gmail
            messages = self.search_gmail(gmail_filter, max_emails)
            
            if not messages:
                return True, "No matching emails found", {
                    'emails_processed': 0,
                    'attachments_uploaded': 0
                }
            
            # Process messages
            total_attachments = 0
            uploaded_files = []
            
            for message_info in messages:
                message_id = message_info['id']
                
                # Get full message
                message = self.get_message_details(message_id)
                if not message:
                    continue
                
                # Extract attachments
                attachments = self.extract_attachments(message)
                
                # Upload to Drive
                for filename, data in attachments:
                    file_id, link = self.upload_to_drive(
                        filename, 
                        data, 
                        target_folder_id
                    )
                    
                    if file_id:
                        total_attachments += 1
                        uploaded_files.append({
                            'filename': filename,
                            'file_id': file_id,
                            'link': link
                        })
            
            summary = f"Processed {len(messages)} emails, uploaded {total_attachments} attachments to Drive"
            self.log_info(summary)
            
            return True, summary, {
                'emails_processed': len(messages),
                'attachments_uploaded': total_attachments,
                'files': uploaded_files,
                'drive_folder_id': target_folder_id
            }
            
        except FileNotFoundError as e:
            return False, str(e), {}
        except Exception as e:
            self.log_error(f"Workflow execution failed: {str(e)}")
            return False, f"Failed: {str(e)}", {}