from django.shortcuts import render
from . import http_decorator
import sys

sys.path.insert(1, 'M:/Django Project/sheetuploader/sheetuploader/GoogleSheetPrograms')
import bandq
import homebase
import hornbach_beta
import jtf
import shopdirect
import wayfair
import therange
import travisperkins
import order_well
sys.path.insert(1, 'M:/Django Project/sheetuploader/sheetuploader/DeliveryStatus')
import status_xdp
import status_ukmail

# Create your views here.
def index(request):
    return render(request, 'request_form.html')


@http_decorator.print_http_response
def upload(request):
    if request.method == "POST":
        if 'bandq' in request.POST:
            print('<h1>B & Q Updater:</h1>')
            bandq.main()
        elif 'homebase' in request.POST:
            print('<h1>Homebase Updater:</h1>')
            homebase.main()
        elif 'hornbach' in request.POST:
            print('<h1>Hornbach Updater:</h1>')
            hornbach_beta.main()
        elif 'wayfair' in request.POST:
            print('<h1>Wayfair Updater:</h1>')
            wayfair.main()
        elif 'jtf' in request.POST:
            print('<h1>JTF Updater:</h1>')
            jtf.main()
        elif 'therange' in request.POST:
            print('<h1>Range Updater:</h1>')
            therange.main()
        elif 'travisperkins' in request.POST:
            print('<h1>Travis Perkins Updater:</h1>')
            travisperkins.main()
        elif 'shopdirect' in request.POST:
            print('<h1>Shopdirect Updater:</h1>')
            shopdirect.main()
        elif 'orderwell' in request.POST:
            print('<h1>Orders:</h1>')
            order_well.main()
        else:
            print('Error loading functions')

@http_decorator.print_http_response     
def search(request):
    if request.method == "POST":
        # FORMS TABLE
        print('''
            <table style="width:60%" align="left">
            <tr>
            <th>Date</th>
            <th>Delivery Company</th>
            <th>Account No</th>
            <th>Consignment</th>
            <th>Customer Ref</th>
            <th>Post Code</th>
            <th>Delivery Status</th>
            </tr>
            '''
        )

        # INPUT TO TABLE AFTER

        postcodes = request.POST.get("textfield", None).split(', ')
        status_xdp.main(postcodes)
        status_ukmail.main(postcodes)
        
        # INPUT TO TABLE BEFORE
        print('</table>')
