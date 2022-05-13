from django.shortcuts import render
from django.http import HttpResponse
from .models import *
import json

def index(request):
    pers = []
    for per in Shift.objects.all():
        pers += per.filmingTime
    context = {
        'periods': pers
    }
    return render(request, 'period_viewer/period.html', context)

def login(request):
    return render(request, 'period_viewer/login.html')