from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from datetime import datetime, timedelta

def load_gmail_emails():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv("GOOGLE_CLIENT_SECRET_FILE"), SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('gmail', 'v1', credentials=creds)
    
    one_week_ago = datetime.now() - timedelta(days=7)
    query = f'after:{one_week_ago.strftime("%Y/%m/%d")}'
    
    results = service.users().messages().list(
        userId='me', 
        q=query,
        maxResults=50 
    ).execute()
    
    messages = results.get('messages', [])
    emails = []
    
    print(f"Loading {len(messages)} emails from the last week...")
    
    for message in messages:
        try:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            
            headers = msg.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            snippet = msg.get('snippet', '')
            
            email_content = f"From: {sender}\nSubject: {subject}\nContent: {snippet}"
            emails.append(email_content)
            
        except Exception as e:
            print(f"Error processing email: {e}")
            continue
    
    print(f"Successfully loaded {len(emails)} emails from the last week")
    return emails
