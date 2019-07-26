import sys
from django.http import HttpResponse


def print_http_response(f):
    class WritableObject:
        def __init__(self):
            self.content = []

        def write(self, string):
            self.content.append(string)

    def new_f(*args, **kwargs):
        printed = WritableObject()
        sys.stdout = printed
        f(*args, **kwargs)
        sys.stdout = sys.__stdout__
        
        return HttpResponse(
            [
                '<h1>' + c + '</h1>'
                for c in printed.content
            ]
        )

    return new_f
