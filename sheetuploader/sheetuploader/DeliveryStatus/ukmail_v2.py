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
        
        login_payload = {
          '_VIEWSTATE_Login' : viewstate_login,
          '__VIEWSTATE' : '',
          'btnLogin': 'Log in',
          'txtUsername' : ukmail_login['Username'],
          'txtPassword' : ukmail_login['Password']
        }
        
        r = s.post(login_url, data=login_payload)
        
        for i in range(25):
            consignments_url = 'https://iconsign.ukmail.com/iconsignv5/FindConsignments.aspx?pn=%d' % (i + 1)
            resp = s.get(consignments_url)
            
            soup = BSoup(resp.content, 'html.parser')
            consignment_list = soup.find('table', id='ctl00_mainContent_consignmentGridView')
            
            viewstate = soup.find('input', id='__VIEWSTATE').get('value')
            viewstate_generator = soup.find('input', id='__VIEWSTATEGENERATOR').get('value')
            authToken = soup.find('input', id='ctl00_mainContent_authToken').get('value')
            
            for consignment in consignment_list.find_all('tr'):
                
                td_elements = consignment.find_all('td')
                
                try:
                    consignment_event = td_elements[0].find('a', string='Track').get('id')
                    event_target = re.sub('_', '$', consignment_event)
                except:
                    skip = 'For empty TD elements at start of TABLE'
                
                for postcode in postcodes:
                    for element in td_elements:
                        if postcode in element:
                        
                            consignment_payload = create_payload(event_target,
                                                                 viewstate,
                                                                 viewstate_generator,
                                                                 authToken,
                                                                 ukmail_login)
                        
                            response = s.post(consignments_url, data=consignment_payload)

                            consign_soup = BSoup(response.content, 'html.parser')
                            
                            consign_data = {
                                'status': consign_soup.find('input', id='ctl00_mainContent_txtStatus').get('value'),
                                'date_collected': consign_soup.find('input', id='ctl00_mainContent_txtCollectionDate').get('value'),
                                'consign_no': consign_soup.find('input', id='ctl00_mainContent_txtConNumber').get('value'),
                                'customer_ref': consign_soup.find('input', id='ctl00_mainContent_txtCustomerRef').get('value'),
                                'postcode': postcode
                                }

                            print_html(consign_data)
                                
def create_payload(event_target, viewstate, viewstate_generator, authToken, ukmail_login):

    consignment_payload = {
                            '__EVENTTARGET': event_target,
                            '__EVENTARGUMENT': '',
                            '__VIEWSTATE': viewstate,
                            '__VIEWSTATEGENERATOR': viewstate_generator,
                            'ctl00$mainContent$searchByCombobox': '[Customer ref]',
                            'ctl00$mainContent$searchForTextbox': '',
                            'ctl00$mainContent$Consignment': '',
                            'ctl00$mainContent$ParcelNumber': 0,
                            'ctl00$mainContent$PrinterName': 'None',
                            'ctl00$mainContent$ProformaPrinter': 'None',
                            'ctl00$mainContent$ProformaPrintPreference': False,
                            'ctl00$mainContent$LabelType': '',
                            'ctl00$mainContent$PaperSize': 'Thermal6x4',
                            'ctl00$mainContent$username': ukmail_login['Username'],
                            'ctl00$mainContent$authToken': authToken
                        }

    return consignment_payload


def  print_html(consign_data):

    print('<tr>'
            '<td style="text-align:center">' + consign_data['date_collected'] + '</td>'
            '<td style="text-align:center">UK Mail</td>'
            '<td style="text-align:center">N/a</td>'
            '<td style="text-align:center">' + consign_data['consign_no'] + '</a></td>'
            '<td style="text-align:center">' + consign_data['customer_ref'] + '</td>'
            '<td style="text-align:center">' + consign_data['postcode'] + '</td>'
            '<td style="text-align:center">' + consign_data['status'] + '</td>'
            '</tr>'
            )

        
if __name__ == '__main__':
    main()
