from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import datetime

def load_calendar_events():
    """Load calendar events with proper error handling"""
    
    # Check if Google credentials are configured
    client_secret_file = os.getenv("GOOGLE_CLIENT_SECRET_FILE")
    if not client_secret_file or not os.path.exists(client_secret_file):
        print("WARNING: Google credentials not found. Skipping calendar data loading.")
        return []
    
    try:
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        creds = None
        
        if os.path.exists('token_calendar.json'):
            creds = Credentials.from_authorized_user_file('token_calendar.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token_calendar.json', 'w') as token:
                token.write(creds.to_json())
        
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=now,
            maxResults=10, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        summaries = [event.get('summary', 'No title') for event in events]
        
        print(f"Successfully loaded {len(summaries)} calendar events")
        return summaries
        
    except HttpError as e:
        if "Calendar API has not been used" in str(e) or "accessNotConfigured" in str(e):
            print("ERROR: Google Calendar API is not enabled for your project.")
            print("Please visit: https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview")
            print("Enable the Calendar API and try again.")
        else:
            print(f"ERROR: Google Calendar API error: {e}")
        
        print("Continuing without calendar data...")
        return []
        
    except Exception as e:
        print(f"ERROR: Unexpected error loading calendar data: {e}")
        print("Continuing without calendar data...")
        return []
