from .models import Cart, Wishlist, CATEGORY_CHOICES

def cart_and_wishlist_counts(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = Cart.objects.filter(user=request.user).count()
        wishitem = Wishlist.objects.filter(user=request.user).count()
    
    categories = [
        {'code': code, 'name': name}
        for code, name in CATEGORY_CHOICES
    ]
    
    return {
        'totalitem': totalitem,
        'wishitem': wishitem,
        'nav_categories': categories,
    }
