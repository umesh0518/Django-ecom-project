from django.urls import path
from account import views as AccountViews
from . import views


urlpatterns = [
    path('', AccountViews.custDashboard, name='customer'),
    path('profile/', views.cprofile, name='cprofile'),
    path('my_orders/', views.my_orders, name='customer_my_orders'),
    path('customer_order_detail/<int:order_number>/', views.order_detail, name='customer_order_detail'),
    # path('my_investment/<int:customer_id>/projects/', views.my_investment, name='my_investment'),
    # path('farm_status/<int:id>/', views.cfarm_status, name='cfarm_status'),
]

