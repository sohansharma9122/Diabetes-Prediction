from django.shortcuts import render, redirect

from Home import *
from .models import *
# Create your views here.

def home(request):
    if request.user.is_authenticated:
        print("User logged in hai")
    else:
        print("User login nahi hai")

    return render(request, "home.html")


def contact(request):
    return render(request,"contact.html")


def about(request):
    return render(request,"about.html")


def faq(request):
    return render(request,"faq.html")


def gallary(request):
    return render(request,"gallary.html")


