from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Customer, Product, Cart, Payment, OrderPlaced, Wishlist, CATEGORY_CHOICES
from django.db.models import Count, Q
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.decorators import method_decorator
import razorpay
import uuid

# Helper to map category code to readable name
CATEGORY_DICT = dict(CATEGORY_CHOICES)

def home(request):
    """
    Public Home Page: Showcases hero banners, value propositions,
    category grid, featured dairy products, and organic advantages.
    """
    featured_products = Product.objects.all()[:8]
    best_sellers = Product.objects.all().order_by('-discounted_price')[:4]
    
    # Pre-select representative image and info for each category
    category_cards = []
    for code, name in CATEGORY_CHOICES:
        sample_prod = Product.objects.filter(category=code).first()
        count = Product.objects.filter(category=code).count()
        category_cards.append({
            'code': code,
            'name': name,
            'count': count,
            'image': sample_prod.product_image.url if sample_prod else None,
        })

    context = {
        'featured_products': featured_products,
        'best_sellers': best_sellers,
        'category_cards': category_cards,
    }
    return render(request, "app/home.html", context)


def about(request):
    """Public About Us page"""
    return render(request, "app/about.html")


def contact(request):
    """Public Contact page with submission feedback"""
    if request.method == 'POST':
        messages.success(request, "Thank you for reaching out! Our team will get back to you shortly.")
        return redirect("contact")
    return render(request, "app/contact.html")


class CategoryView(View):
    """
    Public Category Page: Browse products by category with optional sorting.
    """
    def get(self, request, val):
        sort_by = request.GET.get('sort', '')
        products = Product.objects.filter(category=val)
        
        if sort_by == 'price_low':
            products = products.order_by('discounted_price')
        elif sort_by == 'price_high':
            products = products.order_by('-discounted_price')
        elif sort_by == 'name':
            products = products.order_by('title')

        titles = Product.objects.filter(category=val).values('title').distinct()
        category_name = CATEGORY_DICT.get(val, "Products")

        context = {
            'product': products,
            'title': titles,
            'current_category': val,
            'category_name': category_name,
            'sort_by': sort_by,
        }
        return render(request, "app/category.html", context)


class CategoryTitle(View):
    """Filter products by specific title within category"""
    def get(self, request, val):
        products = Product.objects.filter(title=val)
        current_cat = products[0].category if products.exists() else 'ML'
        titles = Product.objects.filter(category=current_cat).values('title').distinct()
        category_name = CATEGORY_DICT.get(current_cat, "Products")

        context = {
            'product': products,
            'title': titles,
            'current_category': current_cat,
            'category_name': category_name,
            'selected_title': val,
        }
        return render(request, "app/category.html", context)


class ProductDetail(View):
    """
    Public Product Detail: Shows product specs, images, pricing,
    wishlist state (if logged in), and related recommendations.
    """
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        is_in_wishlist = False
        if request.user.is_authenticated:
            is_in_wishlist = Wishlist.objects.filter(product=product, user=request.user).exists()
            
        related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

        context = {
            'product': product,
            'wishlist': is_in_wishlist,
            'related_products': related_products,
            'category_name': CATEGORY_DICT.get(product.category, "Dairy"),
        }
        return render(request, "app/productdetail.html", context)


class CustomerRegistrationView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Congratulations! Your account has been created. Please sign in.")
            return redirect('login')
        else:
            messages.warning(request, "Please correct the errors below.")
            return render(request, 'app/customerregistration.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        addresses = Customer.objects.filter(user=request.user)
        return render(request, 'app/profile.html', {'form': form, 'addresses': addresses, 'active': 'profile'})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            reg = Customer(
                user=request.user,
                name=form.cleaned_data['name'],
                locality=form.cleaned_data['locality'],
                city=form.cleaned_data['city'],
                mobile=form.cleaned_data['mobile'],
                state=form.cleaned_data['state'],
                zipcode=form.cleaned_data['zipcode']
            )
            reg.save()
            messages.success(request, "New address successfully added to your profile!")
            return redirect('address')
        else:
            messages.warning(request, "Invalid input data. Please check the fields.")
            addresses = Customer.objects.filter(user=request.user)
            return render(request, 'app/profile.html', {'form': form, 'addresses': addresses, 'active': 'profile'})


@login_required
def address(request):
    addresses = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'add': addresses, 'active': 'address'})


@method_decorator(login_required, name='dispatch')
class updateAddress(View):
    def get(self, request, pk):
        addr = get_object_or_404(Customer, pk=pk, user=request.user)
        form = CustomerProfileForm(instance=addr)
        return render(request, 'app/updateAddress.html', {'form': form, 'address_id': pk})

    def post(self, request, pk):
        addr = get_object_or_404(Customer, pk=pk, user=request.user)
        form = CustomerProfileForm(request.POST, instance=addr)
        if form.is_valid():
            form.save()
            messages.success(request, "Address updated successfully!")
            return redirect("address")
        else:
            messages.warning(request, "Please check the entered values.")
            return render(request, 'app/updateAddress.html', {'form': form, 'address_id': pk})


@login_required
def delete_address(request, pk):
    addr = get_object_or_404(Customer, pk=pk, user=request.user)
    addr.delete()
    messages.success(request, "Address removed successfully.")
    return redirect("address")


@login_required
def add_to_cart(request):
    product_id = request.GET.get('prod_id') or request.POST.get('prod_id')
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_count = Cart.objects.filter(user=request.user).count()
        return JsonResponse({
            'status': 'success',
            'message': f"{product.title} added to cart!",
            'totalitem': cart_count,
        })
    messages.success(request, f"{product.title} added to your cart!")
    return redirect("/cart/")


@login_required
def show_cart(request):
    cart = Cart.objects.filter(user=request.user)
    amount = 0.0
    original_total = 0.0
    for p in cart:
        amount += (p.quantity * p.product.discounted_price)
        original_total += (p.quantity * p.product.selling_price)
    
    # Free shipping on orders above 499, otherwise 40
    shipping = 0.0 if amount >= 499 else (40.0 if amount > 0 else 0.0)
    totalamount = amount + shipping
    savings = original_total - amount

    context = {
        'cart': cart,
        'amount': amount,
        'shipping': shipping,
        'totalamount': totalamount,
        'savings': max(0.0, savings),
        'free_delivery_threshold': 499,
        'remaining_for_free': max(0.0, 499 - amount) if amount > 0 else 499,
    }
    return render(request, 'app/addtocart.html', context)


@method_decorator(login_required, name='dispatch')
class checkout(View):
    def get(self, request):
        addresses = Customer.objects.filter(user=request.user)
        cart_items = Cart.objects.filter(user=request.user)
        
        if not cart_items.exists():
            messages.info(request, "Your cart is currently empty.")
            return redirect('showcart')

        amount = sum(p.quantity * p.product.discounted_price for p in cart_items)
        shipping = 0.0 if amount >= 499 else 40.0
        totalamount = amount + shipping
        razoramount = int(totalamount * 100)

        order_id = f"order_demo_{uuid.uuid4().hex[:12]}"
        razorpay_enabled = False

        # Attempt Razorpay Order Creation if keys are configured
        try:
            if settings.RAZOR_KEY_ID and not settings.RAZOR_KEY_ID.startswith("dummy"):
                client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
                data = {
                    "amount": razoramount,
                    "currency": "INR",
                    "receipt": f"rcpt_{request.user.id}_{uuid.uuid4().hex[:6]}"
                }
                payment_response = client.order.create(data=data)
                order_id = payment_response['id']
                razorpay_enabled = True
        except Exception:
            # Graceful fallback to demo / direct order id
            razorpay_enabled = False

        # Create or update pending payment record
        Payment.objects.create(
            user=request.user,
            amount=totalamount,
            razorpay_order_id=order_id,
            razorpay_payment_status='created',
            paid=False
        )

        context = {
            'add': addresses,
            'cart_items': cart_items,
            'amount': amount,
            'shipping': shipping,
            'totalamount': totalamount,
            'razoramount': razoramount,
            'order_id': order_id,
            'razorpay_enabled': razorpay_enabled,
            'razor_key_id': settings.RAZOR_KEY_ID,
        }
        return render(request, 'app/checkout.html', context)

    def post(self, request):
        """Handle Direct / Cash on Delivery or Test Order submission"""
        cust_id = request.POST.get('custid')
        payment_method = request.POST.get('payment_method', 'cod')
        
        if not cust_id:
            messages.error(request, "Please select or add a shipping address before proceeding.")
            return redirect('checkout')
            
        customer = get_object_or_404(Customer, id=cust_id, user=request.user)
        cart_items = Cart.objects.filter(user=request.user)
        
        if not cart_items.exists():
            messages.warning(request, "No items in cart to checkout.")
            return redirect('showcart')

        amount = sum(p.quantity * p.product.discounted_price for p in cart_items)
        shipping = 0.0 if amount >= 499 else 40.0
        totalamount = amount + shipping

        # Create Payment Record
        payment = Payment.objects.create(
            user=request.user,
            amount=totalamount,
            razorpay_order_id=f"PAY_{payment_method.upper()}_{uuid.uuid4().hex[:10]}",
            razorpay_payment_id=f"TXN_{uuid.uuid4().hex[:12]}",
            razorpay_payment_status='COMPLETED' if payment_method == 'cod' else 'PAID',
            paid=True
        )

        # Place orders for all cart items
        for c in cart_items:
            OrderPlaced.objects.create(
                user=request.user,
                customer=customer,
                product=c.product,
                quantity=c.quantity,
                payment=payment,
                status='Accepted'
            )
            c.delete()

        messages.success(request, "Your order has been placed successfully! Farm-fresh dairy is on its way.")
        return redirect('orders')


@login_required
def payment_done(request):
    """Callback handler after successful Razorpay checkout"""
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id', f'pay_{uuid.uuid4().hex[:8]}')
    cust_id = request.GET.get('cust_id')
    user = request.user

    if not cust_id:
        messages.error(request, "Shipping address was not provided.")
        return redirect('checkout')

    try:
        customer = Customer.objects.get(id=cust_id, user=user)
    except Customer.DoesNotExist:
        messages.error(request, "Customer address not found.")
        return redirect('checkout')

    payment, _ = Payment.objects.get_or_create(
        razorpay_order_id=order_id,
        defaults={'user': user, 'amount': 0, 'paid': False}
    )
    payment.paid = True
    payment.razorpay_payment_id = payment_id
    payment.razorpay_payment_status = 'captured'
    payment.save()

    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced.objects.create(
            user=user,
            customer=customer,
            product=c.product,
            quantity=c.quantity,
            payment=payment,
            status='Accepted'
        )
        c.delete()

    messages.success(request, "Payment received! Your order is confirmed and being prepared.")
    return redirect("orders")


@login_required
def orders(request):
    order_placed = OrderPlaced.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'app/orders.html', {'order_placed': order_placed})


@login_required
def wishlist(request):
    """Dedicated Wishlist page to view and move items to cart"""
    items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'app/wishlist.html', {'wishlist_items': items})


@login_required
def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        c = get_object_or_404(Cart, product_id=prod_id, user=request.user)
        c.quantity += 1
        c.save()

        cart = Cart.objects.filter(user=request.user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        shipping = 0.0 if amount >= 499 else 40.0
        totalamount = amount + shipping

        return JsonResponse({
            'quantity': c.quantity,
            'item_total': c.total_cost,
            'amount': amount,
            'shipping': shipping,
            'totalamount': totalamount,
        })


@login_required
def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        c = get_object_or_404(Cart, product_id=prod_id, user=request.user)
        if c.quantity > 1:
            c.quantity -= 1
            c.save()
            new_qty = c.quantity
        else:
            c.delete()
            new_qty = 0

        cart = Cart.objects.filter(user=request.user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        shipping = 0.0 if amount >= 499 or amount == 0 else 40.0
        totalamount = amount + shipping

        return JsonResponse({
            'quantity': new_qty,
            'item_total': (new_qty * c.product.discounted_price) if new_qty > 0 else 0,
            'amount': amount,
            'shipping': shipping,
            'totalamount': totalamount,
        })


@login_required    
def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET.get('prod_id')
        Cart.objects.filter(product_id=prod_id, user=request.user).delete()

        cart = Cart.objects.filter(user=request.user)
        amount = sum(p.quantity * p.product.discounted_price for p in cart)
        shipping = 0.0 if amount >= 499 or amount == 0 else 40.0
        totalamount = amount + shipping
        totalitem = cart.count()

        return JsonResponse({
            'status': 'success',
            'amount': amount,
            'shipping': shipping,
            'totalamount': totalamount,
            'totalitem': totalitem,
        })


@login_required
def plus_wishlist(request):
    prod_id = request.GET.get('prod_id') or request.POST.get('prod_id')
    product = get_object_or_404(Product, id=prod_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    wishitem_count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({
        'status': 'added',
        'message': f"{product.title} added to Wishlist",
        'wishitem_count': wishitem_count,
    })


@login_required
def minus_wishlist(request):
    prod_id = request.GET.get('prod_id') or request.POST.get('prod_id')
    product = get_object_or_404(Product, id=prod_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    wishitem_count = Wishlist.objects.filter(user=request.user).count()
    return JsonResponse({
        'status': 'removed',
        'message': f"{product.title} removed from Wishlist",
        'wishitem_count': wishitem_count,
    })


def search(request):
    """Public Search: Searches title, description, and composition"""
    query = request.GET.get('search', '').strip()
    if query:
        products = Product.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) | 
            Q(composition__icontains=query)
        ).distinct()
    else:
        products = Product.objects.none()

    context = {
        'product': products,
        'query': query,
        'result_count': products.count(),
    }
    return render(request, "app/search.html", context)