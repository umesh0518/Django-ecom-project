from django.http import JsonResponse
from django.shortcuts import render
from account.models import VisitorCount
from shop.models import Product


def index(request):
    visitor_count, created = VisitorCount.objects.get_or_create(id=1)
    visitor_count.count += 1
    visitor_count.save()

    # Fetch 5 most recently added products
    recent_products = Product.objects.filter(is_available=True).order_by('-created_at')[:5]

    print("Recent Products:", recent_products)  # Debug print to check fetched products

    context = {
        'recent_products': recent_products,
    }
    return render(request, 'index.html', context)


