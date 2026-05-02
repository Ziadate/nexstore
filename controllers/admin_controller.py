"""
admin_controller.py - Admin dashboard routes.
Blueprint: 'admin', URL prefix: /admin

Admin login uses the users table (role='admin') with werkzeug password hashing.
"""
from flask import (Blueprint, render_template, redirect, url_for,
                   request, flash, jsonify, session)
from functools import wraps
from werkzeug.security import check_password_hash
from models.product import (get_all_products, get_product_by_id,
                             add_product, update_product, delete_product,
                             get_all_categories, get_product_count)
from models.order import (get_all_orders, update_order_status, get_order_count,
                          get_total_revenue, get_orders_by_category,
                          get_orders_by_payment_method, get_revenue_trend)
from models.user import get_all_users
from models.database import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ── Auth decorator ─────────────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin login required.', 'warning')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated


# ── /admin → redirect ──────────────────────────────────────────────────────────
@admin_bp.route('/')
def index():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('admin.admin_login'))


# ── Login ──────────────────────────────────────────────────────────────────────
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()

        print(f"[ADMIN] Login attempt: email={email!r}")

        # Query admin user from DB
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND role = 'admin'",
            (email,)
        ).fetchone()
        conn.close()

        if user:
            print(f"[ADMIN] Found user id={user['id']} role={user['role']}")
            if check_password_hash(user['password_hash'], password):
                # Success — set session
                session.clear()
                session['admin_logged_in'] = True
                session['admin_email']     = email
                session['user_id']         = user['id']
                session['role']            = 'admin'
                print("[ADMIN] LOGIN OK")
                flash('Welcome back, Admin!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                print("[ADMIN] Wrong password")
        else:
            print(f"[ADMIN] No admin user found for email={email!r}")

        flash('Invalid email or password. Please try again.', 'danger')

    return render_template('admin/login.html')


# ── Logout ─────────────────────────────────────────────────────────────────────
@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out of admin panel.', 'info')
    return redirect(url_for('admin.admin_login'))


# ── Dashboard ──────────────────────────────────────────────────────────────────
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    products      = get_all_products()
    orders        = get_all_orders(limit=10)
    users         = get_all_users()
    categories    = get_all_categories()
    total_revenue = get_total_revenue()
    order_count   = get_order_count()
    product_count = get_product_count()
    user_count    = len(users)

    cat_data       = get_orders_by_category()
    cat_labels     = [r['name'] for r in cat_data]
    cat_values     = [r['count'] for r in cat_data]

    pay_data       = get_orders_by_payment_method()
    pay_labels     = [(r['payment_method'] or 'OTHER').upper() for r in pay_data]
    pay_values     = [r['count'] for r in pay_data]

    rev_trend      = get_revenue_trend(7)
    revenue_labels = [r['day'] for r in rev_trend]
    revenue_values = [round(r['revenue'], 2) for r in rev_trend]

    return render_template(
        'admin/dashboard.html',
        products=products,
        orders=orders,
        users=users,
        categories=categories,
        total_revenue=total_revenue,
        order_count=order_count,
        product_count=product_count,
        user_count=user_count,
        cat_labels=cat_labels,
        cat_values=cat_values,
        pay_labels=pay_labels,
        pay_values=pay_values,
        revenue_labels=revenue_labels,
        revenue_values=revenue_values,
    )


# ── Orders ─────────────────────────────────────────────────────────────────────
@admin_bp.route('/orders')
@admin_required
def orders():
    conn = get_db()
    all_orders = conn.execute("""
        SELECT o.id, o.total_price, o.status, o.payment_method,
               o.address, o.created_at,
               u.name AS user_name, u.email AS user_email
        FROM orders o
        JOIN users u ON o.user_id = u.id
        ORDER BY o.created_at DESC
    """).fetchall()
    orders_with_items = []
    for order in all_orders:
        items_data = conn.execute("""
            SELECT oi.quantity, oi.price, p.name AS product_name
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        """, (order['id'],)).fetchall()
        orders_with_items.append({
            'order': dict(order), 
            'order_items': [dict(i) for i in items_data]
        })
    conn.close()
    return render_template('admin/orders.html', orders_with_items=orders_with_items)


@admin_bp.route('/orders/status', methods=['POST'])
@admin_required
def update_order():
    order_id = request.form.get('order_id', type=int)
    status   = request.form.get('status', '').strip()
    valid    = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    if order_id and status in valid:
        update_order_status(order_id, status)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'status': status})
        flash(f'Order #{order_id} updated to "{status}".', 'success')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False}), 400
        flash('Invalid update.', 'danger')
    return redirect(url_for('admin.orders'))


# ── Users ──────────────────────────────────────────────────────────────────────
@admin_bp.route('/users')
@admin_required
def users():
    conn = get_db()
    users_data = conn.execute("""
        SELECT u.id, u.name, u.email, u.role, u.created_at,
               COUNT(o.id) AS order_count,
               COALESCE(SUM(o.total_price), 0) AS total_spent
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """).fetchall()
    conn.close()
    
    # Fix: Convert Rows to dicts for JSON serialization
    users_list = [dict(u) for u in users_data]
    return render_template('admin/users.html', users=users_list)


# ── Products ───────────────────────────────────────────────────────────────────
@admin_bp.route('/products')
@admin_required
def products():
    # Fix Error 1: Convert Rows to dicts for JSON serialization (tojson filter)
    prods = [dict(p) for p in get_all_products()]
    cats  = [dict(c) for c in get_all_categories()]
    return render_template('admin/products.html',
                           products=prods,
                           categories=cats)


@admin_bp.route('/products/add', methods=['POST'])
@admin_required
def add_product_route():
    name        = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    price       = request.form.get('price', type=float)
    old_price   = request.form.get('old_price', type=float)
    category_id = request.form.get('category_id', type=int)
    image_url   = request.form.get('image_url', '').strip()
    stock       = request.form.get('stock', 10, type=int)
    is_featured = 1 if request.form.get('is_featured') else 0
    is_deal     = 1 if request.form.get('is_deal') else 0
    if not name or not price or not category_id:
        flash('Name, price and category are required.', 'danger')
        return redirect(url_for('admin.products'))
    if not image_url:
        image_url = f'https://picsum.photos/seed/{name.replace(" ", "")}/600/600'
    add_product(name, description, price, old_price, category_id,
                image_url, stock, is_featured, is_deal)
    flash(f'Product "{name}" added.', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/products/edit/<int:product_id>', methods=['POST'])
@admin_required
def edit_product_route(product_id):
    name        = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    price       = request.form.get('price', type=float)
    old_price   = request.form.get('old_price', type=float)
    category_id = request.form.get('category_id', type=int)
    image_url   = request.form.get('image_url', '').strip()
    stock       = request.form.get('stock', type=int)
    is_featured = 1 if request.form.get('is_featured') else 0
    is_deal     = 1 if request.form.get('is_deal') else 0
    update_product(product_id, name, description, price, old_price,
                   category_id, image_url, stock, is_featured, is_deal)
    flash(f'Product "{name}" updated.', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/products/delete/<int:product_id>', methods=['POST'])
@admin_required
def delete_product_route(product_id):
    p = get_product_by_id(product_id)
    if p:
        delete_product(product_id)
        flash(f'Product "{p["name"]}" deleted.', 'info')
    return redirect(url_for('admin.products'))


@admin_bp.route('/api/product/<int:product_id>')
@admin_required
def get_product_api(product_id):
    p = get_product_by_id(product_id)
    if not p:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({
        'id':          p['id'],
        'name':        p['name'],
        'description': p['description'] or '',
        'price':       p['price'],
        'old_price':   p['old_price'] or '',
        'category_id': p['category_id'],
        'image_url':   p['image_url'] or '',
        'stock':       p['stock'],
        'is_featured': p['is_featured'],
        'is_deal':     p['is_deal'],
    })
