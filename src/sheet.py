import os
from googleapiclient.discovery import build
from .config import required

HEADERS = ['Name', 'Status', 'YouTube URL', 'Uploaded Date', 'Job ID', 'Updated At', 'Error']

class Sheet:
    def __init__(self, credentials):
        self.api = build('sheets', 'v4', credentials=credentials, cache_discovery=False).spreadsheets().values()
        self.id = required('GOOGLE_SHEET_ID')
        self.tab = "'" + os.getenv('GOOGLE_SHEET_TAB', 'Names').replace("'", "''") + "'"
    def rows(self):
        rows = self.api.get(spreadsheetId=self.id, range=f'{self.tab}!A:I').execute(num_retries=3).get('values', [])
        if not rows or rows[0][:7] != HEADERS:
            raise ValueError('Sheet row 1 must match the seven README headers exactly.')
        if len(rows[0]) > 7 and rows[0][7:] != ['Type', 'Duration Seconds'][:len(rows[0])-7]:
            raise ValueError('Optional columns H and I must be Type and Duration Seconds.')
        return [(i, (row + [''] * 9)[:9]) for i, row in enumerate(rows[1:], 2) if row and row[0].strip()]
    def write(self, number, row):
        self.api.update(spreadsheetId=self.id, range=f'{self.tab}!A{number}:G{number}',
                        valueInputOption='RAW', body={'values': [row[:7]]}).execute(num_retries=3)
