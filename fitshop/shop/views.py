from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
import os
import pyrebase
import datetime
import firebase_admin
from firebase_admin import auth as firebase_admin_auth
from firebase_admin import firestore
from firebase_admin import db as firebase_admin_db
import json
import uuid
import random
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.conf import settings
from pathlib import Path
from firebase_admin import storage as firebase_admin_storage
from firebase_admin import credentials
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponse
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
import colorsys
from decouple import Config, Csv

config = Config()


# from .additional_functions import generate_color

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


# from .additional_functions import divide_sentences
FIREBASE_CONFIG = {
    "apiKey": config("FIREBASE_API_KEY"),
    "authDomain": config("FIREBASE_AUTH_DOMAIN"),
    "projectId": config("FIREBASE_PROJECT_ID"),
    "storageBucket": config("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": config("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": config("FIREBASE_APP_ID"),
    "measurementId": config("FIREBASE_MEASUREMENT_ID"),
    "databaseURL": config("FIREBASE_DATABASE_URL"),
}


BASE_DIR = Path(__file__).resolve().parent.parent

import pyrebase

firebase_config = {
    "apiKey": FIREBASE_CONFIG["apiKey"],
    "authDomain": FIREBASE_CONFIG["authDomain"],
    "databaseURL": FIREBASE_CONFIG["databaseURL"],
    "storageBucket": FIREBASE_CONFIG["storageBucket"],
    "messagingSenderId": FIREBASE_CONFIG["messagingSenderId"],
    "appId": FIREBASE_CONFIG["appId"],
}
cred = credentials.Certificate(os.path.join(BASE_DIR, 'google_service_account.json'))
firebase_admin.initialize_app(cred, {'storageBucket': FIREBASE_CONFIG["storageBucket"]})

firebase_pyrebase = pyrebase.initialize_app(firebase_config)

pyrebase_auth=firebase_pyrebase.auth()

firebase_admin_cloud=firestore.client()

pyrebase_db=firebase_pyrebase.database()

pyrebase_storage=firebase_pyrebase.storage()

def index(request):
    items_variable=pyrebase_db.child('products').get()
    items=[]
    for item in items_variable.each():
        items.append(item.val())
    
    paginator=Paginator(items,12)
    page=request.GET.get('page')
    
    items=paginator.get_page(page) 
    
    return render(request, 'index.html',)



def register(request):
    if request.method == "POST":
        email=request.POST.get('email')
        first_name=request.POST.get('first_name')
        second_name=request.POST.get('second_name')
        password=request.POST.get('password')            #reemeber to add fuctionality since we using the user class
        password2=request.POST.get('password2')
        if password==password2:
            try:
                user=pyrebase_auth.create_user_with_email_and_password(email,password)
                pyrebase_auth.send_email_verification(user['idToken'])
                verification_sent_time=datetime.datetime.now()
                data={'first_name':first_name,
                      'second_name':second_name,
                      'verification_sent_time':verification_sent_time}
                
                user_id=user['localId']
                
                user_ref = firebase_admin_cloud.collection('users').document(str(user_id))
                user_ref.collection('User_info').document().set(data)
                
                
                print('ok2222')
                
                messages.info(request, 'email verification sent please go confirm your email to avoid account closing')
                return redirect('login')
            except:
                messages.info(request, 'email already exists')
                print('email already exists')
                return redirect('register')
        else:
            messages.info(request, 'passwords not matching')
            print('passwords not matching')
            return redirect('register')   
      
        
        
        
    
    return render(request, 'register.html')



def logout(request):

    del request.session['uid']
    
    return redirect('index')

def forgotpassword(request):
    if request.method == "POST":
        email=request.POST.get('email')
        pyrebase_auth.send_password_reset_email(email)
    
    return render(request, 'forgotpassword.html')

def login_user(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        account_info=firebase_admin_auth.get_user_by_email(email)
        if  account_info.disabled:
            return redirect('enable_account')

        else:
            user=pyrebase_auth.sign_in_with_email_and_password(email,password)
            session_id=user['localId']
            request.session['uid']=str(session_id)
            return redirect('index')
        
            

    return render(request, 'login.html')




def enable_account(request):
    if request.method=="POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        user_firebase=firebase_admin_auth.get_user_by_email(email)
        user = firebase_admin_auth.update_user(user_firebase.uid, disabled=False)
        user_pyrebse=pyrebase_auth.sign_in_with_email_and_password(email,password)
        id_token = user_pyrebse['idToken']
        pyrebase_auth.send_email_verification(id_token)
        messages.info(request, 'email verification sent please go confirm your email')
        user_id=user_pyrebse['localId']
        user_ref = firebase_admin_cloud.collection('users').document(user_id)
        user_doc = user_ref.get()
        user_data = user_doc.to_dict()
        user_data['verification_sent_time'] = datetime.datetime.now()

    
        user_ref.set(user_data)
        # place message for sucessful email sent
        return redirect('login')
    return render(request, 'enable_account.html')


# when user signs up remeber to add roles to prevent access to admin pages

def add_product(request):
    if request.method == "POST" or request.method == "FILES":
        item_id=str(uuid.uuid4())
        sku=str(uuid.uuid4())
        name = request.POST.get('name')  #add a way to add csv file to uplod items
        category = request.POST.get('category')
        
        gender = request.POST.get('gender')
        size = request.POST.get('size')
        colour = request.POST.get('colour')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        description = request.POST.get('description')
        weight=request.POST.get('weight')
        brand=request.POST.get('brand')
        material=request.POST.get('material')
        secondary_description=request.POST.get('secondarydescription')
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')
        image5 = request.FILES.get('image5')
        image6 = request.FILES.get('image6')

        # Upload images to Firebase Storage and retrieve public URLs
        
        imageUrl1 = None
        if image1:
            image_path = "products/" + name + "/image1.jpg"
            pyrebase_storage.child(image_path).put(image1, token='YOUR_USER_TOKEN')
            imageUrl1 = pyrebase_storage.child(image_path).get_url(None)
            messages.info(request, 'please wait while we upload your images 1/6')
        imageUrl2 = None
        if image2:
            image_path = "products/" + name + "/image2.jpg"
            pyrebase_storage.child(image_path).put(image2, token='YOUR_USER_TOKEN')
            imageUrl2 = pyrebase_storage.child(image_path).get_url(None)
            messages.info(request, 'please wait while we upload your images 2/6')
        imageUrl3 = None
        if image3:
            image_path = "products/" + name + "/image3.jpg"
            pyrebase_storage.child(image_path).put(image3, token='YOUR_USER_TOKEN')
            imageUrl3 = pyrebase_storage.child(image_path).get_url(None)
            messages.info(request, 'please wait while we upload your images 3/6')
        imageUrl4 = None
        if image4:
            image_path = "products/" + name + "/image4.jpg"
            pyrebase_storage.child(image_path).put(image4, token='YOUR_USER_TOKEN')
            imageUrl4 = pyrebase_storage.child(image_path).get_url(None)
            messages.info(request, 'please wait while we upload your images 4/6')
        imageUrl5 = None
        if image5:
            image_path = "products/" + name + "/image5.jpg"
            pyrebase_storage.child(image_path).put(image5, token='YOUR_USER_TOKEN')
            imageUrl5 = pyrebase_storage.child(image_path).get_url(None)
            messages.info(request, 'please wait while we upload your images 5/6')
        imageUrl6 = None
        if image6:
            image_path = "products/" + name + "/image6.jpg"
            pyrebase_storage.child(image_path).put(image6, token='YOUR_USER_TOKEN')
            imageUrl6 = pyrebase_storage.child(image_path).get_url(None)
            messages.info(request, 'please wait while we upload your images 6/6')
        # Save the data to Firestore
        
        product_ref = pyrebase_db.child("products").child(item_id)
        product_ref.set({
            'Item_id':item_id,
            'name': name,
            'sku': sku,
            'category': category,
            'gender': gender,
            'colour':colour,
            'size': size,
            'price': price,
            'quantity': quantity,
            'description': description,
            'imageUrl1': imageUrl1,
            'imageUrl2': imageUrl2,
            'imageUrl3': imageUrl3,
            'imageUrl4': imageUrl4,
            'imageUrl5': imageUrl5,
            'imageUrl6': imageUrl6,
            'weight':weight,
            'brand':brand,
            'material':material,
            'secondarydescription':secondary_description,
        })
        messages.success(request, 'Product added successfully')

    return render(request, 'add_product.html')

def item_description(request,item_id):
    item=pyrebase_db.child('products').child(item_id).get()
    
    item_data = item.val()
    name = item_data.get('name')
    category = item_data.get('category')
    price = item_data.get('price')
    colour = item_data.get('colour')
    material = item_data.get('material')
    brand = item_data.get('brand')
    secondary_description = item_data.get('secondarydescription')
    description = str(item_data.get('description'))
    image1 = item_data.get('imageUrl1')
    image2 = item_data.get('imageUrl2')
    image3 = item_data.get('imageUrl3')
    image4 = item_data.get('imageUrl4')
    image5 = item_data.get('imageUrl5')
    image6 = item_data.get('imageUrl6')

    item_data = {
        'name': name,
        'description': description,
        'category': category,
        'price': price,
        'colour': colour,
        'brand': brand,
        'material': material,
        'secondarydescription': secondary_description,
        'image1': image1,
        'image2': image2,
        'image3': image3,
        'image4': image4,
        'image5': image5,
        'image6': image6,
    }

    category_items = []
    products_ref = pyrebase_db.child('products')

    # Iterate over child nodes under the 'products' parent node
    for child in products_ref.get().each():
        item = child.val()
        if item.get('category') == category:
            category_items.append(item)

    
    category_items = [item for item in category_items if item != item_data]

    
    random_items = random.sample(category_items, min(4, len(category_items)))

    
    item_data['similar_items'] = []
    for random_item in random_items:
        similar_item_data = {
            'image': random_item.get('imageUrl1'),
            'name': random_item.get('name'),
            'description': random_item.get('description'),
            'price': random_item.get('price'),
        }
        item_data['similar_items'].append(similar_item_data)
    
    return render(request, 'item_description.html',item_data)

def add_to_wishlist(request):
    
    return render(request, 'add_to_wishlist.html')

def shop(request):
    items_variable=pyrebase_db.child('products').get()
    items=[]
    for item in items_variable.each():
        items.append(item.val())
        
    context={'items':items}
    
    return render(request, 'shop.html',context)

def get_random_items(request):
    items_variable = pyrebase_db.child('products').get()
    items = []
    for item in items_variable.each():
        items.append(item.val())
    
    random.shuffle(items)  # Shuffle the items to get random order
    random_items = items[:5]
    if random_items==None:
        print('yes nothing')               # Get the first 5 random items (adjust the number as needed)
    
    return JsonResponse({'items': random_items})


# def search(request):
#     if request.method == 'POST':
#         word = request.POST.get('search')

#         search_results = []
#         products_ref = pyrebase_db.child('products')
#         query = products_ref.order_by_child('name').equal_to(word)
#         docs = query.get()
#         for doc in docs.each():
#             search_results.append(doc.val())
#             print("Item found by name:", doc.val()['name'])
        
#         print("Search results after name query:", search_results)

#         if not search_results:
#             # If no results found by name, search by color
#             query = products_ref.order_by_child('color').equal_to(word)  # Match color
#             docs = query.get()
#             for doc in docs.each():
#                 search_results.append(doc.val())
#                 print("Item found by color:", doc.val()['name'])

#         print("Search results after color query:", search_results)

#         if not search_results:
#             # If still no results found, search by size
#             query = products_ref.order_by_child('size').equal_to(word)  # Match size
#             docs = query.get()
#             for doc in docs.each():
#                 search_results.append(doc.val())
#                 print("Item found by size:", doc.val()['name'])

#         print("Final search results:", search_results)

#         return render(request, 'search.html', {'results': search_results})

#     return render(request, 'search.html')
# use this because of the code update
def search(request):
    if request.method == 'POST':
        word = request.POST.get('search')
        search_results = []
        products_ref = pyrebase_db.child('products')  # Assuming 'products' is the parent node
     
        # Iterate over child nodes under the 'products' parent node
        for child in products_ref.get().each():
            item = child.val()
        
            item_name = item.get('name', '').lower()  # Get item name with a default value of ''
            item_color = item.get('color', '').lower()  # Get item color with a default value of ''
            item_size = item.get('size', '').lower() # Get item size with a default value of ''
            print(item_name, item_color, item_size)

            if word in item_name or word in item_color or word in item_size:
                search_results.append(item)
                print("Item found:", item_name)

        print("Final search results:", search_results)

        return render(request, 'search.html', {'results': search_results})

    return render(request, 'search.html')






def add_to_cart(request):
    user_id=request.session.get('uid')
    users_cart=pyrebase_db.child('cart').child(user_id).child('items').get()
    if users_cart.val()==None:
        pyrebase_db.child('cart').child(user_id).child('items').set({})
        print('cart created')
        if request.method=='POST':
            data = json.loads(request.body)
            size = data.get('size')          #add such that the product whem added and it has some properties (size,colour)then its sku is added to the cart 
            item_id = data.get('item_id')
            
            
            
            quantity = data.get('quantity')
            print(quantity)
            
            item=pyrebase_db.child('products').child(item_id).get()
            item_data=item.val()
            database_quantity=item_data.get('quantity')
            
            if int(quantity)>int(database_quantity):
                messages.error(request, 'Sorry, we only have '+database_quantity+' items in stock')
                print('Sorry, we only have '+database_quantity+' items in stock')
                return redirect('item_description',item_id=item_id)

            else:
                price=item_data.get('price')
                totalprice=(int(quantity)*int(price))
                cart_id=uuid.uuid4().hex[:10]
                items={ 
                        'item_id':item_id,
                       'size':size,
                       'quantity':quantity,
                       'totalprice':totalprice}
                string_of_itemid=str(item_id)
                
                pyrebase_db.child('cart').child(user_id).child('items').child(string_of_itemid).set(items)
                pyrebase_db.child('cart').child(user_id).child('totalprice').set(totalprice)
                print('Item added to cart')
    else:
        if request.method=='POST':
            data = json.loads(request.body)
            size = data.get('size')
            item_id = data.get('item_id')
            quantity = data.get('quantity')
            
            cart_items=pyrebase_db.child('cart').child(user_id).child('items').get()
            
            # firebase_admin_items=firebase_admin_db.reference('cart').child(user_id).child('items').get()
            
            # cart_item=pyrebase_db.child('cart').child('items').get()
            # for cart_item_key, cart_item_data in firebase_admin_items.items():
            #     cartitem_id = cart_item_data.get('item_id')
            # cartdata=cart_items.val()
            # print(cartdata)
                
            
            for cart_item_data in cart_items.val().items():
                cartitem_id = cart_item_data[1]['item_id']
                # quantity = cart_item_data[1]['quantity']
                # totalprice = cart_item_data[1]['totalprice']
                

                
                
                if item_id==cartitem_id:
                    
                    messages.error(request, 'Item already in cart')
                    print('Item already in cart')
                    return redirect('itemdescription',item_id=item_id)
                else:
                    product_item=pyrebase_db.child('products').child(item_id).get()
                    item_data=product_item.val()
                    
                    price=item_data.get('price')
                    item_id=item_data.get('name')#remember to change this to item_id
                    database_quantity=item_data.get('quantity')
                    integer_quantity=int(quantity)
                    integer_database_quantity=int(database_quantity)
                    if integer_quantity > integer_database_quantity:
                        messages.error(request, 'Sorry, we only have '+database_quantity+' items in stock')
                        print('Sorry, we only have number '+database_quantity+' items in stock'+'you put'+quantity)
                        return redirect('itemdescription',item_id=item_id)
                    else:   
                        addtional_totalprice=(int(quantity)*int(price))
                        existing_items=pyrebase_db.child('cart').child(user_id).child('items').get()
                        get_totalprice=pyrebase_db.child('cart').child(user_id).child('totalprice').get()
                        existing_items_data=existing_items.val()
                        get_totalprice_data=get_totalprice.val()
                        existing_totalprice=get_totalprice_data
                        
                        new_total_price=(int(existing_totalprice)+int(addtional_totalprice))
                        # new_item_key = pyrebase_db.child('cart').child(user_id).child('items').child(item_id).push().key
                        new_item = {
                        'item_id': item_id,
                        'quantity': quantity,
                        'price': price,
                        'size': size,
                        }
                        pyrebase_db.child('cart').child(user_id).child('items').child(item_id).set(new_item)

                        # Update the total price in the cart
                        pyrebase_db.child('cart').child(user_id).update({'totalprice': new_total_price})
                        print('Item added to cart')

    return render(request, 'cart.html')

def remove_from_cart(request):
    #put message for sucessful removal from cart
    return render(request, 'remove_from_cart.html')

def remove_from_wishlist(request):
    #put message for sucessful removal from wishlist
    return render(request, 'remove_from_wishlist.html')

def cart(request):
    user_id=request.session.get('uid')
    users_cart=pyrebase_db.child('cart').child(user_id).child('items').get()
    cart_total=pyrebase_db.child('cart').child(user_id).child('totalprice').get()
    cart_total_data=cart_total.val()
    if users_cart.val()==None:
        print('Cart is empty')
        return render(request,'cart.html')
    
    else:
        items=[]
    
        for  item_data in users_cart.each():
            item=item_data.val()
            item_id = item['item_id']
            item['item_id']=item_id
            item['item_total']=item['totalprice']
            
            
            
            # Fetch additional details for the item based on the item ID
            item_details = pyrebase_db.child('products').child(item_id).get().val()
            
            if item_details is not None:
                item['name'] = item_details['name']
                item['colour']=item_details['colour']  
                # item['item_total']=item_details['totalprice']
                
            
                item['price'] = item_details['price']
                
                item['imageUrl1'] = item_details['imageUrl1']
            items.append(item)
    
        

    return render(request, 'template_creater.html',{'items': items,'cart_total_data':cart_total_data})

def shipping_details(request):
    user_id=request.session.get('uid')
    if request.method=='POST':
        first_name=request.POST.get('first_name')
        second_name=request.POST.get('last_name')
        adressing1=request.POST.get('addressing1')
        adressing2=request.POST.get('addressing2')
        postal_code=request.POST.get('postcode')
        city=request.POST.get('city')
        country=request.POST.get('country')
        
        
        data={'first_name':first_name,
              'second_name':second_name,
              'adressing1':adressing1,
              'adressing2':adressing2,
              'postal_code':postal_code,
              'city':city,
              'country':country}
        
        user_ref = firebase_admin_cloud.collection('users').document(str(user_id))

        # Set the shipping information document within the user's document
        user_ref.collection('Shipping_info').document().set(data)
        
        
        
    return render(request, 'shippingdetails.html')


def orders (request):
    return render(request, 'orders.html')

def process_payment(request):
    user_id=request.session.get('uid')
    order = pyrebase_db.child('cart').child(user_id).child('items').get()
    
    totalammount=pyrebase_db.child('cart').child(user_id).child('totalprice').get()
    totalammount_data=totalammount.val()
    host = request.get_host()
    for cart_item_data in order.val().items():
            item_name = cart_item_data[0]
            item_data = cart_item_data[1]
            cart_item_id = item_data['item_id']
            quantity = item_data['quantity']
            item_got=pyrebase_db.child('products').child(cart_item_id).get()
            item_got_data=item_got.val()
            name=item_got_data['name']
            price=item_got_data['price']
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': totalammount_data,
        'item_name': name,
        'invoice': name,
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host,
                                           reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,
                                           reverse('payment_done')),
        'cancel_return': 'http://{}{}'.format(host,
                                              reverse('payment_cancelled')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'process_payment.html', {'order': order, 'form': form})

@csrf_exempt
def payment_done(request):
    #delete cart from firestore
    user_id=request.session.get('uid')
    pyrebase_db.child('cart').child(user_id).remove()
    return render(request, 'payment_done.html')


@csrf_exempt
def payment_canceled(request):
    return render(request, 'payment_cancelled.html')


def checkout(render):
    return redirect('process_payment')

def template(request):
    user_id=request.session.get('uid')
    users_cart=pyrebase_db.child('cart').child(user_id).child('items').get()
    cart_total=pyrebase_db.child('cart').child(user_id).child('totalprice').get()
    cart_total_data=cart_total.val()
    if users_cart.val()==None:
        print('Cart is empty')
        return render(request,'cart.html')
    
    else:
        items=[]
    
        for  item_data in users_cart.each():
            item=item_data.val()
            item_id = item['item_id']
            item['item_total']=item['totalprice']
            
            
            
            # Fetch additional details for the item based on the item ID
            item_details = pyrebase_db.child('products').child(item_id).get().val()
            
            if item_details is not None:
                item['name'] = item_details['name']
                item['colour']=item_details['colour']  
                # item['item_total']=item_details['totalprice']
                
            
                item['price'] = item_details['price']
                
                item['imageUrl1'] = item_details['imageUrl1']
            items.append(item)
    
        

    return render(request, 'template_creater.html',{'items': items,'cart_total_data':cart_total_data})

def add_quantity(request,item_id):
    
    item_id = request.POST.get('item_id')
    user_id=request.session.get('uid')
    cart_item=pyrebase_db.child('cart').child(user_id).child('items').child(item_id).get()
    number=1
    cart_item_data=cart_item.val()
    product=pyrebase_db.child('products').child(item_id).get()
    product_data=product.val()
    item_price=product_data['price']
    cart_quantity=cart_item_data['quantity']
    original_items_total=item_price*cart_quantity
    
    newcart_quantity=cart_quantity+number
    cartitem_ref=pyrebase_db.child('cart').child(user_id).child('items').child(item_id)
    carttotal_ref=pyrebase_db.child('cart').child(user_id).child('totalprice')
    cartitem_ref.update({'quantity':newcart_quantity})
    cart_total=pyrebase_db.child('cart').child(user_id).child('totalprice').get()
    cart_total_data=cart_total.val()
    newcart_totalholder=cart_total_data-original_items_total


    holder_value=item_price*newcart_quantity
    newcart_total=holder_value+newcart_totalholder
    
    carttotal_ref.update({'totalprice':newcart_total})
    return redirect('cart')
    

def reduce_quantity(request, item_id):
    
    item_id = item_id
    user_id=request.session.get('uid')
    print(user_id)
    cart_item=pyrebase_db.child('cart').child(user_id).child('items').child(item_id).get()
    number=1
    cart_item_data=cart_item.val()
    product=pyrebase_db.child('products').child(item_id).get()
    product_data=product.val()
    if product_data==None:
        print('product is none')
    else:
        item_price=product_data['price']
        cart_quantity=cart_item_data['quantity']
        original_items_total=int(item_price)*int(cart_quantity)
        
        newcart_quantity=int(cart_quantity)-int(number)
        cartitem_ref=pyrebase_db.child('cart').child(user_id).child('items').child(item_id)
        carttotal_ref=pyrebase_db.child('cart').child(user_id).child('totalprice')
        string_newcart_quantity=str(newcart_quantity)
        
        cart_total=pyrebase_db.child('cart').child(user_id).child('totalprice').get()
        print(cart_total)
        print(cart_total.val())
        if cart_total==None:
            print('cart total is none')
        else:
            cart_total_data=cart_total.val()
            print(cart_total_data)
            newcart_totalholder=cart_total_data-original_items_total


            holder_value=int(item_price)*int(newcart_quantity)
            newcart_total=int(holder_value)+int(newcart_totalholder)
            integer_newcart_total=int(newcart_total)
            try:
                carttotal_ref.update({'totalprice':integer_newcart_total})
                cartitem_ref.update({'quantity':string_newcart_quantity})
            except:
                print('error')
            return redirect('cart')
        
    
    
    