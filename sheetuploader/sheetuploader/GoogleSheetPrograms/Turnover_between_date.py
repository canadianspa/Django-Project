import pickle
import os.path
import requests
import re
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

spreadsheet_id = '1umWNEdhu2Snc61VXVqcFMWUDDb0F-fEBlGQoVInwSkg'

def main(search_date):
    creds = None
    
    apikey_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "GoogleSheetPrograms\\apikey.json")
    credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "GoogleSheetPrograms\\credentials.json")
    token_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "GoogleSheetPrograms\\token.pickle")
    
    with open(apikey_path) as api_key:    
        headers = json.load(api_key)
        
    creds = None
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('sheets', 'v4', credentials=creds)
    
    # GET ORDERS FROM SPREADSHEET
    
    try:
        po_data = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='504161 DSV (GSX tradeweb)!I97:I').execute()

        po_dates = po_data.get('values', [])

        amount = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='504161 DSV (GSX tradeweb)!S97:S').execute()

        amount_exvat = amount.get('values', [])

        amount_plusvat = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='504161 DSV (GSX tradeweb)!C97:C').execute()

        amount_withvat = amount_plusvat.get('values', [])
                            
    except:
        print('Error getting values')

    total = 0
    
    for i in range(len(po_dates)):
        amount_withvat[i].append('0')
        amount_exvat[i].append('0')
        amount_withvat[i][0] = float(amount_withvat[i][0].replace(',', ''))
        
        if (po_dates[i]
            and amount_withvat[i][0] != 0):
             if search_date in po_dates[i][0]:
                 total += float(amount_exvat[i][0])
    
    print_str = 'For ' + search_date + ': £' + str(round(total, 2)) + ' EX VAT'
    print('<p style="font-size:150%;">For 504161 DSV account</p>')
    print('<p style="font-size:150%;">' + print_str + '</p>')
                    
if __name__ == '__main__':
    main()
