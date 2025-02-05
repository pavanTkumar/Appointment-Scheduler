# utils/calendar_utils.py
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
import streamlit as st
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Optional

class GoogleCalendarManager:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.credentials_path = 'credentials.json'
        self.token_path = 'token.pickle'
        self.timezone = pytz.timezone('America/New_York')  # Adjust to your timezone
        self.initialize_calendar()

    def initialize_calendar(self):
        """Initialize Google Calendar API connection"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # Refresh token if expired
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        "credentials.json not found. Please download it from Google Cloud Console"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)
        
        # Get calendar ID
        calendar_list = self.service.calendarList().list().execute()
        self.calendar_id = next(
            calendar['id'] for calendar in calendar_list['items']
            if calendar.get('primary', False)
        )

    def get_calendar_widget(self):
        """Display an interactive calendar widget"""
        st.write("### Select Meeting Date and Time")
        
        # Date selection
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Show next 30 days only
            min_date = datetime.now().date()
            max_date = min_date + timedelta(days=30)
            selected_date = st.date_input(
                "Select Date",
                min_value=min_date,
                max_value=max_date,
                value=min_date
            )

        with col2:
            # Business hours with 30-min slots
            hours = []
            for hour in range(9, 18):  # 9 AM to 5 PM
                hours.extend([
                    f"{hour:02d}:00",
                    f"{hour:02d}:30"
                ])
            selected_time = st.selectbox("Select Time", hours)

        # Combine date and time
        if selected_date and selected_time:
            hour, minute = map(int, selected_time.split(':'))
            selected_datetime = datetime.combine(
                selected_date,
                datetime.min.time().replace(hour=hour, minute=minute)
            )
            return selected_datetime.replace(tzinfo=self.timezone)
        return None

    def check_availability(self, start_time: datetime) -> bool:
        """Check if the selected time slot is available"""
        end_time = start_time + timedelta(minutes=30)
        
        body = {
            'timeMin': start_time.isoformat(),
            'timeMax': end_time.isoformat(),
            'items': [{'id': self.calendar_id}],
        }
        
        events_result = self.service.freebusy().query(body=body).execute()
        busy = events_result['calendars'][self.calendar_id]['busy']
        
        return len(busy) == 0

    def schedule_meeting(
        self,
        start_time: datetime,
        name: str,
        email: str,
        purpose: str
    ) -> Optional[str]:
        """Schedule a meeting and return the event ID if successful"""
        try:
            if not self.check_availability(start_time):
                return None

            end_time = start_time + timedelta(minutes=30)
            
            event = {
                'summary': f"Meeting with {name}",
                'description': purpose,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': str(self.timezone),
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': str(self.timezone),
                },
                'attendees': [
                    {'email': email},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                    }
                },
            }

            event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event,
                conferenceDataVersion=1,
                sendUpdates='all'
            ).execute()

            return event['id']

        except Exception as e:
            print(f"Error scheduling meeting: {str(e)}")
            return None

    def get_next_available_slots(self, num_slots: int = 5) -> List[datetime]:
        """Get next available meeting slots"""
        slots = []
        current = datetime.now(self.timezone)
        
        while len(slots) < num_slots:
            # Skip to next business day if weekend
            if current.weekday() >= 5:
                current += timedelta(days=1)
                continue
                
            # Check business hours (9 AM - 5 PM)
            if 9 <= current.hour < 17:
                if self.check_availability(current):
                    slots.append(current)
                current += timedelta(minutes=30)
            else:
                # Skip to next day at 9 AM
                current = current.replace(
                    hour=9, 
                    minute=0, 
                    second=0, 
                    microsecond=0
                ) + timedelta(days=1)
        
        return slots