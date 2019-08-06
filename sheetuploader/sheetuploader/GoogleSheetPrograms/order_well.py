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

def main():
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
        result_num = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='504161 DSV (GSX tradeweb)!D97:D').execute()

        inv_nums = result_num.get('values', [])
        
        result_date = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='504161 DSV (GSX tradeweb)!G97:G').execute()

        dates = result_date.get('values', [])
        
        result_item = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='504161 DSV (GSX tradeweb)!K97:M').execute()

        items = result_item.get('values', [])

        result_price = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='504161 DSV (GSX tradeweb)!C97:C').execute()

        prices = result_price.get('values', [])

        result_podate = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='504161 DSV (GSX tradeweb)!I97:I').execute()

        podate = result_podate.get('values', [])
                    
    except:
        print('Error getting values')
    
    
    for i in range(len(inv_nums)):
        try:
            prices[i][0] = prices[i][0].replace(',', '')
            prices[i][0] = float(prices[i][0])
        except:
            prices[i].append(0)
            prices[i][0] = 0
        
        dates.append([])
            
        if not dates[i]:
            if (prices[i][0] > 500 and prices[i][0] != 0):
                print(podate[i][0] + ' ' + str(inv_nums[i][0]) + ' : ')
                for item in items[i]:
                    print(item + ', ')

                print("<BR>")
                    
if __name__ == '__main__':
    main()
