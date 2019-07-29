import requests
import re
import json
import os
from calendar import monthrange
from datetime import datetime
from bs4 import BeautifulSoup as BSoup

def main(postcodes):
    
    xdp_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "DeliveryStatus/xdp_payload.json")

    with open(xdp_path) as xdp_payload:    
        payload = json.load(xdp_payload)
        
    now = datetime.now()
    days_month = monthrange(now.year, now.month - 1 )[1]
    
    if now.day > days_month:
        lastmonth = str(now.year) + '-' + str(now.month - 1) + '-28'
    else:
        lastmonth = str(now.year) + '-' + str(now.month - 1) + '-' + str(now.day)
    
    xdp_a = 'http://aws1.xsys.xdp.co.uk/index.php?from=%s&to=%s&dateSearch=manifestDate&caccno=2A479A&consigNo=&refs=&deliveryPostcode=&pcType=del&p=search-customer&' % (lastmonth, now.strftime("%Y-%m-%d"))
    xdp_b = 'http://aws1.xsys.xdp.co.uk/index.php?from=%s&to=%s&dateSearch=manifestDate&caccno=2A479B&consigNo=&refs=&deliveryPostcode=&pcType=del&p=search-customer&' % (lastmonth, now.strftime("%Y-%m-%d"))
    xdp_c = 'http://aws1.xsys.xdp.co.uk/index.php?from=%s&to=%s&dateSearch=manifestDate&caccno=2A479C&consigNo=&refs=&deliveryPostcode=&pcType=del&p=search-customer&' % (lastmonth, now.strftime("%Y-%m-%d"))
    
    login_url = 'https://auth.xdp.co.uk/index.php?p=login' 

    print('''
            <table style="width:70%" align="left">
            <tr>
            <th>Date</th>
            <th>Account No</th>
            <th>Consignment</th>
            <th>Customer Ref</th>
            <th>Post Code</th>
            <th>Delivery Status</th>
            </tr>
            '''
          )
    
    
    with requests.Session() as s:
        try:
            post = s.post(login_url, data=payload)
        except:
            print('<h1> Error Logging In </h1>')
        
        try:
            i = load_account(s, xdp_a, postcodes)
            i += load_account(s, xdp_b, postcodes)
            i += load_account(s, xdp_c, postcodes)
            if i == 0:
                print('<tr><td>No Consignments found</td></tr>')
                
        except:
            print('<h1> Error Loading Orders </h1>')
    
    print('</table>')

def load_account(s, consign_url, postcodes):
        resp = s.get(consign_url)
        soup = BSoup(resp.content, 'html.parser')

        i = 0
        consignments = []
        for consignment in soup.find_all('div', class_="datablock"):
            consign_data = []
            
            for data in consignment.find_all('td'):
                consign_data.append(data.text)
            
            for postcode in postcodes:
                if postcode in consign_data:
                    consign_data[0] = re.sub(r'\r\n ','', consign_data[0])
                    consign_data[10] = re.sub(r'\r\n ','', consign_data[10])
                    consign_data[10] = re.sub('DELIVERED','DELIVERED ', consign_data[10])

                    for con_id in consignment.find_all('a', href=True):
                        href_element = '<a href="' + 'http://aws1.xsys.xdp.co.uk/' + con_id.get('href') + '">'
                    
                    if consign_data[10] == ' --  ':
                        consign_data[10] = 'AWAITING DELIVERY'
                    
                    print('<tr>'
                            '<td style="text-align:center">' + consign_data[0] + '</td>'
                            '<td style="text-align:center">' + consign_data[1] + '</td>'
                            '<td style="text-align:center">' + href_element + consign_data[2] + '</a></td>'
                            '<td style="text-align:center">' + consign_data[3] + '</td>'
                            '<td style="text-align:center">' + consign_data[5] + '</td>'
                            '<td style="text-align:center">' + consign_data[10] + '</td>'
                            '</tr>'
                          )
                    
                    i += 1

        return i
                
        
if __name__ == '__main__':
    main()
