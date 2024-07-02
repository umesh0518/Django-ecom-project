
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from shop.views import contact

urlpatterns = [
    path('', views.index , name="index"),
    path('contact/', contact , name="contact"),
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('shop/', include('shop.urls')),
    path('customers/', include('customers.urls')),
    path('orders/', include('orders.urls')),
    path('vendor/', include('vendor.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)