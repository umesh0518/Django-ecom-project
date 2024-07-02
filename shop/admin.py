from django.contrib import admin
from .models import Category, Product , Cart, Tax , Enquiry



class ProductItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('product_title',)}
    list_display = ('product_title', 'category', 'price', 'is_available', 'updated_at')
    search_fields = ('product_title', 'category__category_name', 'price')
    list_filter = ('is_available',)


admin.site.register(Category)
admin.site.register(Product, ProductItemAdmin)
admin.site.register(Cart)
admin.site.register(Tax)
admin.site.register(Enquiry)
