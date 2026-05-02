"""
order_controller.py - Checkout flow, order success, and user profile.
Blueprint: 'order', URL prefix: /
"""
import os
from flask import (Blueprint, render_template, redirect, url_for,
                   request, session, flash)
from werkzeug.utils import secure_filename
from controllers.auth_controller import login_required
from models.cart import get_cart_items, get_cart_total, get_cart_count, clear_cart
from models.order import (create_order, create_order_items,
                           get_order_by_id, get_user_orders)
from models.product import update_stock, get_product_by_id
from models.user import get_user_by_id, update_user, update_password, get_user_wishlist

order_bp = Blueprint('order', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             'static', 'images', 'avatars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

PROMO_CODES = {'DISCOUNT10': 0.10, 'SAVE20': 0.20}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@order_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Multi-step checkout: collect address and payment then place order."""
    user_id = session['user_id']
    items   = get_cart_items(user_id)

    if not items:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart.view_cart'))

    subtotal = get_cart_total(user_id)
    promo    = session.get('promo_code')
    discount = round(subtotal * PROMO_CODES[promo], 2) if promo and promo in PROMO_CODES else 0
    shipping = 0 if subtotal >= 50 else 9.99
    total    = round(subtotal - discount + shipping, 2)

    if request.method == 'POST':
        # Collect address
        full_name  = request.form.get('full_name', '').strip()
        address    = request.form.get('address', '').strip()
        city       = request.form.get('city', '').strip()
        zip_code   = request.form.get('zip_code', '').strip()
        country    = request.form.get('country', '').strip()
        payment    = request.form.get('payment_method', 'cod')

        if not all([full_name, address, city, zip_code, country]):
            flash('Please fill in all address fields.', 'danger')
            return render_template('checkout/checkout.html',
                                   items=items, subtotal=subtotal,
                                   discount=discount, shipping=shipping,
                                   total=total, cart_count=get_cart_count(user_id))

        full_address = f"{full_name}, {address}, {city}, {zip_code}, {country}"

        # Create order
        order_id = create_order(user_id, total, payment, full_address)

        # Create order items and decrement stock
        order_items_data = [
            {'product_id': item['product_id'],
             'quantity':   item['quantity'],
             'price':      item['price']}
            for item in items
        ]
        create_order_items(order_id, order_items_data)

        for item in items:
            update_stock(item['product_id'], item['quantity'])

        # Clear cart and promo
        clear_cart(user_id)
        session.pop('promo_code', None)

        return redirect(url_for('order.order_success', order_id=order_id))

    user = get_user_by_id(user_id)
    return render_template(
        'checkout/checkout.html',
        items=items,
        subtotal=subtotal,
        discount=discount,
        shipping=shipping,
        total=total,
        user=user,
        cart_count=get_cart_count(user_id)
    )


@order_bp.route('/order/success/<int:order_id>')
@login_required
def order_success(order_id):
    """Show order confirmation page with confetti."""
    order, items = get_order_by_id(order_id)
    if not order or order['user_id'] != session['user_id']:
        flash('Order not found.', 'danger')
        return redirect(url_for('store.home'))
    return render_template(
        'checkout/order_success.html',
        order=order,
        items=items,
        cart_count=0
    )


@order_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile: view/edit info, order history, wishlist."""
    user_id  = session['user_id']
    user     = get_user_by_id(user_id)
    orders   = get_user_orders(user_id)
    wishlist = get_user_wishlist(user_id)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_profile':
            name   = request.form.get('name', '').strip()
            email  = request.form.get('email', '').strip().lower()
            avatar = user['avatar']

            # Handle avatar upload
            file = request.files.get('avatar')
            if file and file.filename and allowed_file(file.filename):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filename = f"user_{user_id}_{secure_filename(file.filename)}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                avatar = filename

            update_user(user_id, name, email, avatar)
            session['user_name'] = name
            flash('Profile updated successfully! ✅', 'success')
            return redirect(url_for('order.profile'))

        elif action == 'change_password':
            current  = request.form.get('current_password', '')
            new_pw   = request.form.get('new_password', '')
            confirm  = request.form.get('confirm_password', '')
            from werkzeug.security import check_password_hash
            if not check_password_hash(user['password_hash'], current):
                flash('Current password is incorrect.', 'danger')
            elif new_pw != confirm:
                flash('New passwords do not match.', 'danger')
            elif len(new_pw) < 6:
                flash('Password must be at least 6 characters.', 'danger')
            else:
                update_password(user_id, new_pw)
                flash('Password changed successfully! 🔒', 'success')
            return redirect(url_for('order.profile'))

    return render_template(
        'profile/profile.html',
        user=user,
        orders=orders,
        wishlist=wishlist,
        cart_count=get_cart_count(user_id)
    )
