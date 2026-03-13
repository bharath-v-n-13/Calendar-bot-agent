import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from memory import notes_store

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Authenticates and returns the Google Calendar API service."""
    creds = None
    # token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("credentials.json is missing! Please create OAuth Client ID for Desktop App in Google Cloud Console and save here.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def add_task(user_id, task):
    """Adds a task or event to Google Calendar using QuickAdd."""
    try:
        service = get_calendar_service()
        # Uses Google's natural language parsing:
        created_event = service.events().quickAdd(
            calendarId='primary',
            text=task
        ).execute()
        
        summary = created_event.get('summary', task)
        start = created_event.get('start', {}).get('dateTime', created_event.get('start', {}).get('date', 'Unknown Data'))
        return f"✅ Added to Google Calendar: *{summary}* (Scheduled: {start})"
        
    except FileNotFoundError as fnf:
         return f"⚙️ Google Calendar is not fully set up yet. (Missing credentials.json)"
    except Exception as e:
        return f"❌ Failed to reach Google Calendar: {str(e)}"

def list_tasks(user_id):
    """Lists the upcoming events from Google Calendar."""
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        
        if not events:
            return "📋 No upcoming events in your Calendar!"
            
        result = ["📋 *Your Upcoming Events (Google Calendar):*"]
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'Busy')
            # Format nicely
            result.append(f"🗓 {start[:16].replace('T', ' ')}: {summary}")
        return "\n".join(result)
        
    except FileNotFoundError:
        return f"⚙️ Google Calendar is not fully set up yet. (Missing credentials.json)"
    except Exception as e:
        return f"❌ Failed to fetch from Google Calendar: {str(e)}"

def delete_task(user_id, task_name):
    """Deletes an upcoming event matching the task_name."""
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', q=task_name, timeMin=now,
                                              maxResults=5, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            return f"❌ Could not find any upcoming event matching '{task_name}' to delete."
        
        event_to_delete = events[0]
        service.events().delete(calendarId='primary', eventId=event_to_delete['id']).execute()
        return f"🗑️ Deleted event: *{event_to_delete.get('summary', 'Unknown')}*"
    except Exception as e:
        return f"❌ Failed to delete event: {str(e)}"

def search_events(user_id, query):
    """Searches upcoming events across all calendars for a query (e.g., festivals)."""
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        
        # Get all calendars
        calendars_result = service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])
        
        all_events = []
        for cal in calendars:
            try:
                events_result = service.events().list(
                    calendarId=cal['id'], q=query, timeMin=now, maxResults=5,
                    singleEvents=True, orderBy='startTime'
                ).execute()
                for event in events_result.get('items', []):
                    event['_calendar_name'] = cal.get('summary', 'Calendar')
                    all_events.append(event)
            except:
                pass
                
        # Sort all matched events by time
        def get_start_time(e):
             return e['start'].get('dateTime', e['start'].get('date'))
             
        all_events.sort(key=get_start_time)
        
        if not all_events:
            return f"📋 No upcoming events found matching '{query}'!"
            
        result = [f"🔍 *Results for '{query}':*"]
        for event in all_events[:10]:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'Busy')
            cal_name = event['_calendar_name']
            result.append(f"🗓 {start[:16].replace('T', ' ')}: {summary} ({cal_name})")
        return "\n".join(result)
        
    except Exception as e:
        return f"❌ Failed to search events: {str(e)}"

def save_note(user_id, note):
    notes_store.setdefault(user_id, []).append({"note": note})
    return "📝 Note saved in memory!"

def list_notes(user_id):
    notes = notes_store.get(user_id, [])
    if not notes:
        return "📓 No notes yet."
    return "\n".join(f"📝 *{i}.* {n['note']}" for i, n in enumerate(notes, 1))

def get_datetime():
    # Use UTC for standard baseline
    now = datetime.datetime.utcnow()
    return f"🕐 Formatted UTC Time: *{now.strftime('%Y-%m-%d %H:%M:%S UTC')}*"
