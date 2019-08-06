import requests
import json
import re
import os
from bs4 import BeautifulSoup as BSoup

def main(postcodes):
    uklogin_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "DeliveryStatus/ukmail_login.json")
    
    with open(uklogin_path) as ukmail_login:    
        ukmail_login = json.load(ukmail_login)
    
    login_url = 'https://iconsign.ukmail.com/iconsignv5/Login.aspx'
    
    with requests.Session() as s:
        get_viewstate = s.get(login_url)
        get_soup = BSoup(get_viewstate.content, 'html.parser')
        viewstate_login = get_soup.find('input', id='_VIEWSTATE_Login').get('value')
        
        payload = {
          '_VIEWSTATE_Login' : viewstate_login,
          '__VIEWSTATE' : '',
          'btnLogin': 'Login',
          'txtUsername' : ukmail_login['Username'],
          'txtPassword' : ukmail_login['Password']
        }

        try:
            r = s.post(login_url, data=payload)
        except:
            print('Error logging in')
        
        consignment_data = []
        
        for i in range(30):
            consignments_url = 'https://iconsign.ukmail.com/iconsignv5/FindConsignments.aspx?pn=%d' % (i + 1)
            resp = s.get(consignments_url)

            soup = BSoup(resp.content, 'html.parser')
            consignment_list = soup.find('table', id='ctl00_mainContent_consignmentGridView')
            
            for consignment in consignment_list.find_all('tr'):
                data = []
                
                for consignment_td in consignment.find_all('td'):
                    data.append(consignment_td.text)

                for postcode in postcodes:
                    try:
                        if postcode in data:
                            consignment_data.append(data)
                    except:
                        skip = 'Skipping non-order <td> element at start of each table'

            if len(consignment_data) == len(postcodes):
                break
    
    if consignment_data:
        for consignment in consignment_data:
            status = get_status(consignment[6])
            print_html(consignment, status)

def get_status(consignment_number):
    url = 'https://track.dhlparcel.co.uk/?con=' + consignment_number + '&nav=1'
    resp = requests.get(url)
        
    soup = BSoup(resp.content, 'html.parser')
    status = soup.find_all('h3')[1].text

    return status


def  print_html(consign_data, status):

    try:
        status = status.replace('Your parcel ' + consign_data[6], '')
        status = status.replace(' is ', '')
        status = status.replace(' has been ', '')
    except:
        print('Error shortening status')
    
    try:
        print('<tr>'
            '<td style="text-align:center">' + consign_data[7] + '</td>'
            '<td style="text-align:center">UK Mail</td>'
            '<td style="text-align:center">N/a</td>'
            '<td style="text-align:center">' + consign_data[6] + '</a></td>'
            '<td style="text-align:center">' + consign_data[4] + '</td>'
            '<td style="text-align:center">' + consign_data[9] + '</td>'
            '<td style="text-align:center">' + status.upper() + '</td>'
            '</tr>'
            )
    except:
        print('Error assigning data')

        
if __name__ == '__main__':
    main()
