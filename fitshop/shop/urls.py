from django.urls import path
from . import views

urlpatterns=[
    path('',views.index,name='index'),
    path('register',views.register,name='register'),
    path('login',views.login_user,name='login'),
    path('logout',views.logout,name='logout'),
    path('forgotpassword',views.forgotpassword,name='forgotpassword'),
    path("enable_account",views.enable_account,name="enable_account"),
    path('addproduct',views.add_product,name='addproduct'),
    path('itemdescription/<str:item_id>/',views.item_description,name='itemdescription'),
    path('addtocart',views.add_to_cart,name='addtocart'),
    path('removefromcart',views.remove_from_cart,name='removefromcart'),
    path('addtowishlist',views.add_to_wishlist,name='addtowishlist'),
    path('removefromwishlist',views.remove_from_wishlist,name='removefromwishlist'),
    path('cart',views.cart,name='cart'),
    path('shippingdetails',views.shipping_details,name='shippingdetails'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('payment-done/', views.payment_done, name='payment_done'),
    path('payment-cancelled/', views.payment_canceled, name='payment_cancelled'),
    # path('wishlist',views.wishlist,name='wishlist'),
    path('shop',views.shop,name='shop'),
    path('get_random_items/',views.get_random_items,name='get_random_items'),
    path('search',views.search,name='search'),
    path('template',views.template,name='template'),
    path('reducecartquantity/<str:item_id>',views.reduce_quantity,name='reducecartquantity'),
    path('increasecartquantity/<str:item_id>',views.add_quantity,name='increasecartquantity'),
    
    
]