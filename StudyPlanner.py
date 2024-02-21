import os.path
import datetime as dt
from datetime import timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import steam
import requests
import tkinter as tk
from tkinter import messagebox


CLIENT_FILE = r"Path to Google Calendar Toekn File json"
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_CLIENT_ADDRESS = "Calendar Clinet Email Address"
CALENDAR_KEY = "Calendar API key"
API_NAME = 'calendar'
API_VERSION = 'v3'

def string_to_datetime(string):
    # Converts an iso8601 date string into a datetime.datetime data type
    date_format = "%Y-%m-%d %H:%M:%S"
    try:
        string_datetime = dt.datetime.strptime(string, date_format)
        return string_datetime
    except ValueError:
        print("Invalid date format. Please use the format YYYY-MM-DD HH:MM:SS.")
        return None

def get_daily_events():
    creds = None
    datetimes_with_duration = []

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
        now = dt.datetime.now().isoformat() + 'Z'
        tmo_temp = dt.datetime.now() + timedelta(days=1)
        tmo = tmo_temp.isoformat() + "Z"
        event_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=tmo,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = event_result.get("items", [])

        if not events:
            print("No events today")
            return

        for event in events:
            if event["summary"] == "Study":
                start_time = event['start'].get('dateTime', event["start"].get("date"))
                end_time = event['end'].get('dateTime', event["end"].get("date"))

            # Parse start and end times as datetime objects
            #     start_time_str = start[:-6]
            #     start_time = string_to_datetime(start_time_str)
            #     end_time_str = end[:-6]
            #     end_time = string_to_datetime(end_time_str)

                # Calculate the duration of the event
                # duration = end_time - start_time

            # Append a tuple containing start time, end time, and duration
                datetimes_with_duration.append((start_time, end_time)) #duration

    except HttpError as error:
        print('An error occurred:', error)

    return datetimes_with_duration


def steam_status():
    # Replace 'YOUR_API_KEY' with your actual Steam API key
    steam_api_key = 'STEAM API KEY'
    steam_user_id = 'YOUR STEAM ACCOUNT ID'  # Replace with the Steam ID of the user you want to query

    url = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steam_api_key}&steamids={steam_user_id}'
    response = requests.get(url)
    data = response.json()

    if 'response' in data and 'players' in data['response']:
        players = data['response']['players']
        if players:
            player = players[0]
            if 'gameid' in player:
                game_id = player['gameid']
                return True
            else:
                return False
    else:
        print('Failed to retrieve player information.')


class ReadyToFocusWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("StudyPlanner")

        self.message_label = tk.Label(root, text="Are you ready to focus?", font=("Helvetica", 14))
        self.message_label.pack(pady=20)

        self.start_button = tk.Button(root, text="Start", command=self.start_study_reminder)
        self.start_button.pack(pady=10)

    def start_study_reminder(self):
        self.root.destroy()


class StudyReminderApp:
    def __init__(self, root, events):
        self.root = root
        self.root.title("StudyPlanner")

        self.message_label = tk.Label(root, text="It's time to study instead of playing video games!", font=("Helvetica", 14))
        self.message_label.pack(pady=20)

        self.close_button = tk.Button(root, text="Close", command=self.close_app)
        self.close_button.pack(pady=10)

        self.events = events
    def close_app(self):
        self.root.destroy()

class NoStudyTimeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("StudyPlanner")

        self.message_label = tk.Label(root, text="No more designated study time. Enjoy your games!", font=("Helvetica", 14))
        self.message_label.pack(pady=20)

        self.close_button = tk.Button(root, text="Close", command=self.close_app)
        self.close_button.pack(pady=10)

    def close_app(self):
        self.root.destroy()


def main():
    os.system("powershell -command \"$shell = New-Object -ComObject Shell.Application; $shell.MinimizeAll()\"")
    try:
        ready_to_focus_root = tk.Tk()
        ready_to_focus_window = ReadyToFocusWindow(ready_to_focus_root)
        ready_to_focus_root.mainloop()

        if ready_to_focus_window:
            events = get_daily_events()
            if events:
                for event in events:
                    condition = True
                    start_time, end_time = event  # duration
                    start_date_str, start_time_str = start_time.split("T")
                    start_time = start_date_str + ' ' + start_time_str[:-6]
                    end_date_str, end_time_str = end_time.split("T")
                    end_time = end_date_str + ' ' + end_time_str[:-6]
                    start_time = string_to_datetime(start_time)
                    end_time = string_to_datetime(end_time)

                    while condition:
                        while start_time < dt.datetime.now() < end_time:
                            if steam_status():
                                root = tk.Tk()
                                study_reminder_app = StudyReminderApp(root, events)  # Pass events here
                                root.mainloop()
                                condition = False
                                break  # Exit the loop once the reminder window is closed
            no_study_time_root = tk.Tk()
            no_study_time_window = NoStudyTimeWindow(no_study_time_root)
            no_study_time_root.mainloop()
        else:
            print("No study events today")  # print this in the output window
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
