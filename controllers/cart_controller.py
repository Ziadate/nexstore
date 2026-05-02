"""
cart_controller.py - Cart view, add/update/remove operations.
Blueprint: 'cart', URL prefix: /cart
"""
from flask import (Blueprint, render_template, redirect, url_for,
                   request, session, flash, jsonify)
from controllers.auth_controller import login_required
from models.cart import (get_cart_items, add_to_cart, update_quantity,
                         remove_from_cart, get_cart_total, get_cart_count)
from models.product import get_product_by_id

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

PROMO_CODES = {
    'DISCOUNT10': 0.10,   # 10% off
    'SAVE20':     0.20,   # 20% off
}


@cart_bp.route('/')
@login_required
def view_cart():
    """Render the cart page with items, totals, and promo code handling."""
    user_id   = session['user_id']
    items     = get_cart_items(user_id)
    subtotal  = get_cart_total(user_id)
    promo     = session.get('promo_code')
    discount  = 0.0
    if promo and promo in PROMO_CODES:
        discount = round(subtotal * PROMO_CODES[promo], 2)

    shipping  = 0 if subtotal >= 50 else 9.99
    total     = round(subtotal - discount + shipping, 2)

    return render_template(
        'cart/cart.html',
        items=items,
        subtotal=subtotal,
        discount=discount,
        shipping=shipping,
        total=total,
        promo_code=promo,
        cart_count=get_cart_count(user_id)
    )


@cart_bp.route('/add', methods=['POST'])
@login_required
def add():
    """Add a product to the cart (AJAX or form POST)."""
    user_id    = session['user_id']
    product_id = request.form.get('product_id', type=int)
    variant_id = request.form.get('variant_id', type=int)
    quantity   = request.form.get('quantity', 1, type=int)

    product = get_product_by_id(product_id)
    if not product:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        flash('Product not found.', 'danger')
        return redirect(url_for('store.home'))

    if product['stock'] < 1:
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Out of stock'}), 400
        flash('Sorry, this item is out of stock.', 'warning')
        return redirect(request.referrer or url_for('store.home'))

    add_to_cart(user_id, product_id, quantity, variant_id)
    new_count = get_cart_count(user_id)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': f'"{product["name"]}" added to cart!',
            'cart_count': new_count
        })

    flash(f'"{product["name"]}" added to cart! 🛒', 'success')
    return redirect(request.referrer or url_for('store.home'))


@cart_bp.route('/update', methods=['POST'])
@login_required
def update():
    """Update the quantity of a cart item."""
    user_id    = session['user_id']
    product_id = request.form.get('product_id', type=int)
    quantity   = request.form.get('quantity', type=int)

    if quantity is not None and product_id:
        update_quantity(user_id, product_id, quantity)

    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/remove', methods=['POST'])
@login_required
def remove():
    """Remove an item from the cart."""
    user_id    = session['user_id']
    product_id = request.form.get('product_id', type=int)
    remove_from_cart(user_id, product_id)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        new_count = get_cart_count(user_id)
        new_total = get_cart_total(user_id)
        return jsonify({'success': True, 'cart_count': new_count, 'new_total': new_total})

    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/promo', methods=['POST'])
@login_required
def apply_promo():
    """Apply or clear a promo code."""
    code = request.form.get('promo_code', '').strip().upper()
    if code in PROMO_CODES:
        session['promo_code'] = code
        pct = int(PROMO_CODES[code] * 100)
        flash(f'Promo code applied: {pct}% off! 🎉', 'success')
    else:
        session.pop('promo_code', None)
        flash('Invalid promo code. Try DISCOUNT10 for 10% off.', 'warning')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/count')
def count():
    """JSON endpoint for live cart badge updates."""
    if 'user_id' in session:
        return jsonify({'count': get_cart_count(session['user_id'])})
    return jsonify({'count': 0})
