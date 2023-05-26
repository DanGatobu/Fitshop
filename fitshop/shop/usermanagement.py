import datetime
import firebase_admin
from .views import config
import pyrebase

firebase=pyrebase.initialize_app(config)

auth=firebase.auth()
database=firebase.database()

def store_verification_sent_time(user_id, verification_sent_time):
    database.child("users").child(user_id).child("verification_sent_time").set(verification_sent_time)


