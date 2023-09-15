from functools import wraps
import firebase_admin
from firebase_admin import auth,credentials
from django.shortcuts import redirect
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

cred=credentials.Certificate(os.path.join(BASE_DIR,'google_service_account.json'),)

firebase_admin.initialize_app(cred,name='decoraters')


def firebase_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if the user is authenticated with Firebase
        if 'uid' not in request.session:
            return redirect('login_user')
        
        # Additional checks or validations can be performed here
        
        # Retrieve the Firebase user ID from the session
        user_id = request.session.get('uid')
        print(user_id)
        
        try:
            # Verify the Firebase user ID
            auth.get_user(user_id)
        except Exception:
            return redirect('login_user')
        
        # User is authenticated, proceed to the view
        return view_func(request, *args, **kwargs)
    
    return wrapper
