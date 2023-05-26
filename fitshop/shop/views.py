from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
# Create your views here.
import pyrebase
import datetime
from firebase_admin import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
# from firebase_admin import auth
from django.conf import settings
import firebase_admin
from firebase_admin import auth, credentials
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
google_client_id = settings.GOOGLE_CLIENT_ID

from urllib.parse import urlencode



config={"apiKey": "AIzaSyBKBq-5zbsHy9M9GZS0iCZCXI7-aN4B1Gk",
  "authDomain": "fitshop-4ce09.firebaseapp.com",
  "projectId": "fitshop-4ce09",
  "storageBucket": "fitshop-4ce09.appspot.com",
  "messagingSenderId": "545964776212",
  "appId": "1:545964776212:web:22999f1945a13e443a0001",
  "measurementId": "G-WLQNPJ7G0Y",
  "databaseURL": "https://fitshop-4ce09-default-rtdb.firebaseio.com"
    
}

firebase=pyrebase.initialize_app(config)

auth=firebase.auth()



def index(request):
    return render(request, 'index.html')



def register(request):
    if request.method == "POST":
        email=request.POST.get('email')
        first_name=request.POST.get('first_name')
        second_name=request.POST.get('second_name')
        password=request.POST.get('password')
        password2=request.POST.get('password2')
        if password==password2:
            try:
                user=auth.create_user_with_email_and_password(email,password)
                auth.send_email_verification(user['idToken'])
                verification_sent_time=datetime.datetime.now()
                messages.info(request, 'email verification sent please go confirm your email')
            except:
                messages.info(request, 'email already exists')
                return redirect('register')
        else:
            messages.info(request, 'passwords not matching')
            return redirect('register')   
        
        
        #firebase use google authentication
        
    
    return render(request, 'register.html')



def logout(request):
    logout(request)
    return redirect('index')


def login(request):
    
    

    return render(request, 'login.html')

@csrf_exempt
def callback(request):
    if request.method == "POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        
        
    

    
    return render(request,"home.html")