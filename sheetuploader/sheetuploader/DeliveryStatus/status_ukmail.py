import requests
import json
import re
import os
from bs4 import BeautifulSoup as BSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
        
        order_data = []
        
        for i in range(20):
            consignments_url = 'https://iconsign.ukmail.com/iconsignv5/FindConsignments.aspx?pn=%d&sb=[Customer+ref]&st=' % (i + 1)
            resp = s.get(consignments_url)

            soup = BSoup(resp.content, 'html.parser')
            consignment_list = soup.find('table', id='ctl00_mainContent_consignmentGridView')
            
            for consignment in consignment_list.find_all('tr'):
                data = ''
                for consignment_td in consignment.find_all('td'):
                    data += consignment_td.text + '|'
                
                order_data.append(data)
                
    consignment_data = []
    consignment_numbers = []
    
    for consignment in order_data:
        check_data = consignment.split('|')
            
        for postcode in postcodes:
            try:
                if postcode in check_data[9]:
                    consignment_data.append(consignment)
                    consignment_numbers.append(check_data[6])
            except:
                skip = 'Skipping non-order <td> element at start of each table'
                
    if consignment_data:
        statuses = get_status(consignment_numbers)
        for consign_str, status in zip(consignment_data, statuses):
            print_html(consign_str, status)


def get_status(consignment_numbers):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # Runs Chrome in headless mode.
    options.add_argument('--disable-gpu')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--test-type")
    options.add_argument("--versions.chrome")
    
    driver = webdriver.Chrome('M:\chromedriver', options=options)
    
    statuses= []
    for consignment_no in consignment_numbers:
        driver.get('https://track.dhlparcel.co.uk/')
        driver.find_element_by_id('LO_01_txtConsignmentNo').send_keys(consignment_no)
        driver.find_element_by_id('LO_01_btnSearch').click()
        
        soup = BSoup(driver.page_source, 'html.parser')
        consignment_status = soup.find_all('h3')[1].text
        statuses.append(consignment_status)
    
    driver.quit()
    
    return statuses


def  print_html(consign_str, status):
    consign_data = consign_str.split('|')

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
