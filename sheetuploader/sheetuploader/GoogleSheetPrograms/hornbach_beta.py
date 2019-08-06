from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
import requests
import re
import json

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

spreadsheet_id = '1Smo5GYQ1BIbiLS3AQczz9UzotLEKEFPdScdRfPMMqgo'

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

    # Forms orders.json of orders today
    now = datetime.now()
    url = ('https://api.veeqo.com/orders?created_at_min=%s&page_size=100' % now.strftime("%Y-%m-%d"))

    try:
        orders = requests.get(url, headers=headers).json() #Veeqo json
        print('<p>Downloaded veeqo json script.</p>')

        # Find last row containing data
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Sheet1!C:C').execute()

    except:
        print('Error downloading Veeqo/Google Script')
    existing_orders = result.get('values', [])
    order_num = re.findall(r'\d+', str(existing_orders))
        
    values = []
    
    for order in orders:
        try:
            firstname = order['customer']['billing_address']['first_name'].upper()
        except error:
            firstname = 'No Address'
            
        if ('HORNBACH' in firstname
            and str(order['id']) not in order_num):
            
            # items list to store items from order
            items = ['','','']
            i = 0
            for sellable in order['line_items']:
                if i > 2:
                    # Append items in orders of more than 3 products to items[2]
                    items[2] = items[2] + ' & ' + sellable['sellable']['product_title'].upper()
                    i+=1
                    
                else:
                    items[i] = sellable['sellable']['product_title'].upper()
                    i+=1
            
            customer_info = order['deliver_to']
            order_date = re.findall(r'\d+', str(order['created_at']))

            po_number = ''
            note_nums = re.findall('\d+', str(order['customer_note']['text']))
            if note_nums:
                for num in note_nums:
                    if len(num) == 10:
                        po_number = num
                        
            try:
                # Creates values list for spreadsheet input data
                values.append (
                    [order_date[2]+'/'+order_date[1]+'/'+order_date[0],
                    '',
                    order['number'],
                    po_number,
                    customer_info['first_name'] + ' ' + customer_info['last_name'],
                    customer_info['address1'],
                    items[0] + ' ' + items[1] + ' ' + items[2],
                    '','',
                    order['subtotal_price'],
                    '',
                    order['total_price']
                    ])
            except:
                print('Error appending values')
                        
            if order['status'] == 'cancelled':
                print('<p>Cancelled order ' + order['number'] + ' not uploaded</p>')
                del values[-1]
            
            else:
                print('<p>Order ' + order['number']+ ' uploaded.</p>')

            
    if values:
        # Appending to sheets
        body = {
            'values': values
        }
            
        range_str = 'Sheet1!A' + str(len(existing_orders) + 1) + ':V'
        value_input_option = 'RAW'

        try:  
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_str, # Append order to next row
                valueInputOption=value_input_option,
                body=body).execute()
        except:
            print('Error appending values')
    
    else:
        print('<p>No orders uploaded :(</p>')

if __name__ == '__main__':
    main()
