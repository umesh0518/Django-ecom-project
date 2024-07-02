from django.urls import path
from . import views

 
urlpatterns =[
    path('shop/' , views.shop_view,name='shop'),
    path('product_detail/<int:id>/' , views.product_detail,name='product_detail'),
    path('cart/' , views.cart,name='cart'),
    path('checkout/' , views.checkout,name='checkout'),
    path('get_cart_details/', views.get_cart_details, name='get_cart_details'),
     # ADD TO CART
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    # DECREASE CART
    path('decrease_cart/<int:product_id>/', views.decrease_cart, name='decrease_cart'),
    # DELETE CART ITEM
    path('delete_cart/<int:cart_id>/', views.delete_cart, name='delete_cart'),


]