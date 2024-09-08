from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

# Load Google Sheets API credentials
SERVICE_ACCOUNT_FILE = './thematic-bloom-435018-i8-3c7ff0126a74.json'  # Update with your JSON key file path
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# The ID and range of the spreadsheet.
SPREADSHEET_ID = '1Q7No9vRqBTFZOBYQWZBPF1kqsSD93D1eDfrJPB7Fkdo'  # Replace with your Google Sheet ID
RANGE_NAME = 'Sheet1'

def append_to_sheet(name, email, phone, program, gpa, cmat_score, scholarship):
    values = [[name, email, phone, program, gpa, cmat_score, scholarship]]
    body = {
        'values': values
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',  # This ensures data is appended, not overwritten
        body=body
    ).execute()
    print(f"{result.get('updates').get('updatedCells')} cells updated.")
