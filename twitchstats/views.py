from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView


# Create your views here.

def index(request):
    return HttpResponse('Hello this is website.')


class IndexView(TemplateView):
    template_name = "index.html"
    txt = "default"
    text = "default"

    def wutu(self):
        return 'eksdee'



