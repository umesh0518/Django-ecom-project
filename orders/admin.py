from django.contrib import admin
from .models import Payment, Order, ProductOrder

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number','total' , 'created_at', 'user')


admin.site.register(Payment)
admin.site.register(Order , OrderAdmin)
admin.site.register(ProductOrder)