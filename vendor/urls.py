from django.urls import path, include
from . import views
from account import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vprofile, name='vprofile'),

    path('product_builder/', views.product_builder, name='product_builder'),
    path('product_category/<int:pk>/', views.productItem_by_category, name='product_category'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:pk>/', views.edit_product, name='edit_product'),
    path('delete_producte/<int:pk>/', views.delete_product, name='delete_product'),

    path('my_orders/', views.my_orders, name='vendor_my_orders'),
    path('vendor_order_detail/<int:order_number>/', views.order_detail, name='vendor_order_detail'),
]
