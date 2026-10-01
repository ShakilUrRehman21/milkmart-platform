/**
 * MilkMart E-Commerce Platform - Client Interactive Script
 * Handles real-time cart adjustments, wishlist toggling, and toast feedback.
 */

// Toast notification helper
function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `dairy-toast toast-${type}`;
    const iconClass = type === 'success' ? 'fa-circle-check text-success' : 'fa-circle-info text-primary';
    toast.innerHTML = `<i class="fa-solid ${iconClass} fs-5"></i> <span>${message}</span>`;
    
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.transition = 'all 0.3s ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3200);
}

// Plus Cart Quantity
$(document).on('click', '.plus-cart', function(e) {
    e.preventDefault();
    const btn = $(this);
    const id = btn.attr("pid");
    const qtyElem = btn.siblings('.qty-val');
    const row = btn.closest('.cart-card-item');

    $.ajax({
        type: "GET",
        url: "/pluscart/",
        data: { prod_id: id },
        success: function(data) {
            qtyElem.text(data.quantity);
            if (row.find('.item-line-total').length) {
                row.find('.item-line-total').text('₹' + data.item_total.toFixed(2));
            }
            $('#amount').text('₹' + data.amount.toFixed(2));
            $('#shipping-amount').text(data.shipping === 0 ? 'FREE' : '₹' + data.shipping.toFixed(2));
            $('#totalamount').text('₹' + data.totalamount.toFixed(2));
        },
        error: function() {
            showToast('Unable to update cart quantity', 'error');
        }
    });
});

// Minus Cart Quantity
$(document).on('click', '.minus-cart', function(e) {
    e.preventDefault();
    const btn = $(this);
    const id = btn.attr("pid");
    const qtyElem = btn.siblings('.qty-val');
    const row = btn.closest('.cart-card-item');

    $.ajax({
        type: "GET",
        url: "/minuscart/",
        data: { prod_id: id },
        success: function(data) {
            if (data.quantity <= 0) {
                row.fadeOut(300, function() {
                    $(this).remove();
                    if ($('.cart-card-item').length === 0) {
                        location.reload();
                    }
                });
            } else {
                qtyElem.text(data.quantity);
                if (row.find('.item-line-total').length) {
                    row.find('.item-line-total').text('₹' + data.item_total.toFixed(2));
                }
            }
            $('#amount').text('₹' + data.amount.toFixed(2));
            $('#shipping-amount').text(data.shipping === 0 ? 'FREE' : '₹' + data.shipping.toFixed(2));
            $('#totalamount').text('₹' + data.totalamount.toFixed(2));
        },
        error: function() {
            showToast('Unable to update cart quantity', 'error');
        }
    });
});

// Remove Item from Cart
$(document).on('click', '.remove-cart', function(e) {
    e.preventDefault();
    const btn = $(this);
    const id = btn.attr("pid");
    const row = btn.closest('.cart-card-item');

    $.ajax({
        type: "GET",
        url: "/removecart/",
        data: { prod_id: id },
        success: function(data) {
            row.fadeOut(300, function() {
                $(this).remove();
                if ($('.cart-card-item').length === 0) {
                    location.reload();
                }
            });
            $('#amount').text('₹' + data.amount.toFixed(2));
            $('#shipping-amount').text(data.shipping === 0 ? 'FREE' : '₹' + data.shipping.toFixed(2));
            $('#totalamount').text('₹' + data.totalamount.toFixed(2));
            
            // Update cart badge in navbar
            const badge = $('#nav-cart-badge');
            if (data.totalitem > 0) {
                badge.text(data.totalitem).show();
            } else {
                badge.hide();
            }
            showToast('Item removed from cart');
        },
        error: function() {
            showToast('Unable to remove item', 'error');
        }
    });
});

// Add to Wishlist Toggle
$(document).on('click', '.plus-wishlist', function(e) {
    e.preventDefault();
    const btn = $(this);
    const id = btn.attr("pid");

    $.ajax({
        type: "GET",
        url: "/pluswishlist/",
        data: { prod_id: id },
        success: function(data) {
            btn.removeClass('plus-wishlist text-muted')
               .addClass('minus-wishlist active text-danger');
            btn.find('i').removeClass('fa-regular').addClass('fa-solid');

            const badge = $('#nav-wish-badge');
            if (data.wishitem_count > 0) {
                badge.text(data.wishitem_count).show();
            }
            showToast(data.message || 'Saved to Wishlist!');
        },
        error: function(xhr) {
            if (xhr.status === 403 || xhr.status === 401 || xhr.status === 302) {
                window.location.href = '/accounts/login/?next=' + window.location.pathname;
            } else {
                showToast('Please sign in to save wishlist items', 'error');
            }
        }
    });
});

// Remove from Wishlist Toggle
$(document).on('click', '.minus-wishlist', function(e) {
    e.preventDefault();
    const btn = $(this);
    const id = btn.attr("pid");
    const isWishlistPage = btn.closest('.wishlist-page-card').length > 0;

    $.ajax({
        type: "GET",
        url: "/minuswishlist/",
        data: { prod_id: id },
        success: function(data) {
            if (isWishlistPage) {
                btn.closest('.wishlist-page-card').fadeOut(300, function() {
                    $(this).remove();
                    if ($('.wishlist-page-card').length === 0) {
                        location.reload();
                    }
                });
            } else {
                btn.removeClass('minus-wishlist active text-danger')
                   .addClass('plus-wishlist text-muted');
                btn.find('i').removeClass('fa-solid').addClass('fa-regular');
            }

            const badge = $('#nav-wish-badge');
            if (data.wishitem_count > 0) {
                badge.text(data.wishitem_count).show();
            } else {
                badge.hide();
            }
            showToast(data.message || 'Removed from Wishlist');
        },
        error: function() {
            showToast('Unable to update wishlist', 'error');
        }
    });
});

// Quick Add to Cart via AJAX (from product card)
$(document).on('click', '.ajax-add-cart', function(e) {
    e.preventDefault();
    const btn = $(this);
    const id = btn.attr('data-prod-id');
    const originalHtml = btn.html();

    btn.html('<i class="fa-solid fa-spinner fa-spin"></i> Adding...');

    $.ajax({
        type: 'GET',
        url: '/add-to-cart/',
        data: { prod_id: id },
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        success: function(data) {
            btn.html('<i class="fa-solid fa-check"></i> Added!');
            const badge = $('#nav-cart-badge');
            badge.text(data.totalitem).show();
            showToast(data.message || 'Added to cart successfully!');
            setTimeout(() => {
                btn.html(originalHtml);
            }, 1800);
        },
        error: function(xhr) {
            btn.html(originalHtml);
            if (xhr.status === 302 || xhr.status === 401 || xhr.status === 403) {
                window.location.href = '/accounts/login/?next=' + window.location.pathname;
            } else {
                // Fallback to standard form redirect
                window.location.href = '/add-to-cart/?prod_id=' + id;
            }
        }
    });
});
