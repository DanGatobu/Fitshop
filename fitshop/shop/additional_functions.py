import firebase_admin
from firebase_admin import auth,credentials,firestore
import datetime
import colorsys
cloud_storage=firestore.client()

def generate_color(word):
    # Convert the word to a numerical value
    value = sum(ord(char) for char in word)
    
    # Normalize the value between 0 and 1
    normalized_value = value / 255.0
    
    # Convert the normalized value to an RGB color
    rgb_color = colorsys.hsv_to_rgb(normalized_value, 1, 1)
    
    # Convert the RGB color to a hex color code
    hex_color = '#%02x%02x%02x' % tuple(int(c * 255) for c in rgb_color)
    
    return hex_color



def check_user_verification():
    users = auth.list_users().iterate_all()
    for user in users:
        user_id=user.uid
        verification_time_sent_refrence=cloud_storage.collection('users').document(user_id).document('user_info')
        verification_time_sent_holding=verification_time_sent_refrence.get()
        verification_time_sent=verification_time_sent_holding('verification_sent_time')
        datetime_now=datetime.datetime.now()
        time_passed=datetime_now-verification_time_sent
        if time_passed.days > 3:
            verification_status=user.email_verified
            if verification_status==False:
                auth.update_user(user_id, disabled=True)
                
# def enable_user():
#     users = auth.list_users().iterate_all()
#     for user in users:
#         user_id=user.uid
        
        
#         verification_status=user.email_verified
#         if verification_status==True:
#             auth.update_user(user_id, disabled=False)
    
# def divide_sentences(block_of_words):
#     # Split the block of words into sentences using full stop as the delimiter
#     sentences = block_of_words.split('. ')
    
#     # Calculate the total number of sentences
#     num_sentences = len(sentences)
    
#     # Calculate the number of sentences per division
#     sentences_per_division = num_sentences // 3
    
#     # Divide the sentences into three parts
#     divisions = [sentences[i:i+sentences_per_division] for i in range(0, num_sentences, sentences_per_division)]
    
#     return divisions
