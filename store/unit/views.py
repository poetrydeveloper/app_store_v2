# app user views

from django.shortcuts import render



def home_view(request):
    return render(request, 'store/home.html')

def main_view(request):
    return render(request, 'store/main.html')