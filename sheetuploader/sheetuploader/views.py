from django.shortcuts import render
from . import http_decorator
import sys

sys.path.insert(1, 'M:/Django/sheetuploader/sheetuploader/UploadPrograms')
import bandq
import homebase
import hornbach_beta
import jtf
import shopdirect
sys.path.insert(1, 'M:/Django/sheetuploader/sheetuploader/DeliveryStatus')
import checkstatus

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
        elif 'jtf' in request.POST:
            print('<h1>JTF Updater:</h1>')
            jtf.main()
        elif 'shopdirect' in request.POST:
            print('<h1>Shopdirect Updater:</h1>')
            shopdirect.main()
        else:
            print('Error loading functions')

@http_decorator.print_http_response     
def search(request):
    if request.method == "POST":
        postcodes = request.POST.get("textfield", None).split(', ')
        checkstatus.main(postcodes)
    
