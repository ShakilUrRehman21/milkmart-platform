from django.contrib import admin
from .models import Product, Customer, Cart, Payment, OrderPlaced, Wishlist
from django.utils.html import format_html
from django.urls import reverse

@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'discounted_price', 'selling_price', 'category', 'product_image_preview']
    list_filter = ['category']
    search_fields = ['title', 'description', 'composition']

    def product_image_preview(self, obj):
        if obj.product_image:
            return format_html('<img src="{}" width="40" height="40" style="object-fit:contain; border-radius:6px; border:1px solid #ddd;" />', obj.product_image.url)
        return "-"
    product_image_preview.short_description = "Image"

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'mobile', 'city', 'state', 'zipcode']
    search_fields = ['name', 'mobile', 'city', 'locality', 'user__username']
    list_filter = ['state', 'city']

@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product_link', 'quantity', 'total_cost']
    search_fields = ['user__username', 'product__title']

    def product_link(self, obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('<a href="{}"><strong>{}</strong></a>', link, obj.product.title)
    product_link.short_description = "Product"

@admin.register(Payment)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'razorpay_order_id', 'razorpay_payment_status', 'razorpay_payment_id', 'paid']
    list_filter = ['paid', 'razorpay_payment_status']
    search_fields = ['razorpay_order_id', 'razorpay_payment_id', 'user__username']

@admin.register(OrderPlaced)
class OrderPlacedModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'customer_info', 'product_link', 'quantity', 'ordered_date', 'status', 'payment_status']
    list_filter = ['status', 'ordered_date']
    search_fields = ['user__username', 'customer__name', 'customer__mobile', 'product__title', 'payment__razorpay_order_id']
    list_editable = ['status']
    date_hierarchy = 'ordered_date'
    ordering = ['-ordered_date']

    def product_link(self, obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('<a href="{}"><strong>{}</strong></a>', link, obj.product.title)
    product_link.short_description = "Product"

    def customer_info(self, obj):
        link = reverse("admin:app_customer_change", args=[obj.customer.pk])
        return format_html('<a href="{}">{} ({})</a>', link, obj.customer.name, obj.customer.city)
    customer_info.short_description = "Customer"

    def payment_status(self, obj):
        if obj.payment and obj.payment.paid:
            return format_html('<span style="color:#059669; font-weight:bold;">Paid (₹{})</span>', obj.payment.amount)
        return format_html('<span style="color:#d97706; font-weight:bold;">Pending / COD</span>')
    payment_status.short_description = "Payment"

@admin.register(Wishlist)
class WishlistModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product_link']
    search_fields = ['user__username', 'product__title']

    def product_link(self, obj):
        link = reverse("admin:app_product_change", args=[obj.product.pk])
        return format_html('<a href="{}"><strong>{}</strong></a>', link, obj.product.title)
    product_link.short_description = "Product"