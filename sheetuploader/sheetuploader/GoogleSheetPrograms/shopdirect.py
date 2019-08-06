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

spreadsheet_id = '1gUU4RqsU2YKpzEcbH8h9Uao6sjAklylyxs2D51F-RWU'

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
    url = ('https://api.veeqo.com/orders?tags=Shop Direct&page_size=100&created_at_min=%s-01-01' % now.year)

    try:
        orders = requests.get(url, headers=headers).json() #Veeqo json
        print('<p>Downloaded veeqo json script.</p>')

        # Find last row containing data
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range='Shop Direct!D:D').execute()
    except:
        print('Error downloading Veeqo/Google Script')
    
    existing_orders = result.get('values', [])
    order_num = re.findall(r'\d+', str(existing_orders))

    values= []
    
    for order in orders:
        if str(order['id']) not in order_num:
            
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
            order_date = re.findall('\d+', str(order['created_at']))
    
            po_num = ''
            note_nums = re.findall('\d+', str(order['customer_note']['text']))
            if note_nums:
                for num in note_nums:
                    if len(num) == 8:
                        po_num = num                    

            try:
                # Creates values list for spreadsheet input data
                values.append (
                    ['','',
                    order['total_price'],
                    order['number'],
                    po_num,
                    '','','',
                    order_date[2]+'/'+order_date[1]+'/'+order_date[0],
                    '',
                    items[0],items[1],items[2],
                    customer_info['first_name'].upper(),
                    customer_info['last_name'].upper(),
                    customer_info['zip'].upper(),
                    customer_info['address1'].upper()
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
                
        range_str = 'Shop Direct!A'+str(len(existing_orders))+':S'
        value_input_option = 'RAW'

        try:
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_str, # Append order to next row
                valueInputOption=value_input_option,
                body=body).execute()
        except:
            print('Error uploading to sheets')
                
        print('Order ' + order['number']+ ' uploaded.')
    
    else:
        print('<p>No orders uploaded :(</p>')

if __name__ == '__main__':
    main()
