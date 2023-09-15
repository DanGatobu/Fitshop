from django.db import models

from decimal import Decimal
from typing import Iterable

from django.urls import reverse
from .views import pyrebase_db




# class Payment(BasePayment):

#     def get_failure_url(self) -> str:
#         # Return a URL where users are redirected after
#         # they fail to complete a payment:
#         return reverse('payment_failure', kwargs={'pk': self.pk})

#     def get_success_url(self) -> str:
#         # Return a URL where users are redirected after
#         # they successfully complete a payment:
#         return reverse('payment_success', kwargs={'pk': self.pk})

#     def get_purchased_items(self,request) -> Iterable[PurchasedItem]:
#         # Return items that will be included in this payment.
#         user_id=request.session['uid']
#         cart_items=pyrebase_db.child('cart').child(user_id).child('items').get()
#         # cart_item=pyrebase_db.child('cart').child('items').get()
#             # for cart_item_key, cart_item_data in firebase_admin_items.items():
#             #     cartitem_id = cart_item_data.get('item_id')
#             # cartdata=cart_items.val()
#             # print(cartdata)
                
            
#         for cart_item_data in cart_items.val().items():
#             item_name = cart_item_data[0]
#             item_data = cart_item_data[1]
#             cart_item_id = item_data['item_id']
#             quantity = item_data['quantity']
#             item_got=pyrebase_db.child('products').child(cart_item_id).get()
#             item_got_data=item_got.val()
#             name=item_got_data['name']
#             price=item_got_data['price']#ensure you change in the save item such that it will be saved as a float
            
            
        
        
#             yield PurchasedItem(
#                 name=name,
#                 sku='BSKV',
#                 quantity=quantity,
#                 price=price,#here check how it should be correctly done,
#                 currency='USD',
#             )
