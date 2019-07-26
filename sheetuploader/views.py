from django.shortcuts import render
from . import http_decorator
import sys

sys.path.insert(1, 'M:/Django/sheetuploader/sheetuploader/UploadPrograms')
import bandq
import homebase
import hornbach_beta
import jtf
import shopdirect

# Create your views here.
def index(request):
    return render(request, 'google_form.html')


@http_decorator.print_http_response
def upload(request):
    if 'bandq' in request.POST:
        print('B & Q Updater:')
        bandq.main()
    elif 'homebase' in request.POST:
        print('Homebase Updater:')
        homebase.main()
    elif 'hornbach' in request.POST:
        print('Hornbach Updater:')
        hornbach_beta.main()
    elif 'jtf' in request.POST:
        print('JTF Updater:')
        jtf.main()
    elif 'shopdirect' in request.POST:
        print('Shopdirect Updater:')
        shopdirect.main()
    else:
        print('Error loading functions')
        

    
