from django.shortcuts import render

from services.views import ensure_sample_services


def home(request):
    ensure_sample_services()
    return render(request,'home.html')

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')