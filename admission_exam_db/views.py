from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello this is admission exam db app!")

def login(request):
    return HttpResponse("Hello this is login page!")
