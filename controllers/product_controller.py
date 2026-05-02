"""
product_controller.py - Home page, product detail, category, and search views.
Blueprint: 'store', URL prefix: /
"""
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, jsonify)
from models.product import (get_all_categories, get_featured_products,
                             get_todays_deals, get_best_sellers,
                             get_product_by_id, get_products_by_category,
                             get_category_by_slug, search_products,
                             get_related_products, get_all_products)
from models.database import get_db
from models.cart import get_cart_count
from models.user import is_in_wishlist

store_bp = Blueprint('store', __name__)


def _cart_count():
    """Helper to get current user's cart item count for navbar badge."""
    if 'user_id' in session:
        return get_cart_count(session['user_id'])
    return 0


@store_bp.route('/')
def home():
    """Render the main landing/home page."""
    categories   = get_all_categories()
    featured     = get_featured_products(8)
    deals        = get_todays_deals(6)
    best_sellers = get_best_sellers(10)
    return render_template(
        'store/home.html',
        categories=categories,
        featured=featured,
        deals=deals,
        best_sellers=best_sellers,
        cart_count=_cart_count()
    )


@store_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """Render product detail page."""
    product = get_product_by_id(product_id)
    if not product:
        return render_template('404.html'), 404

    related = get_related_products(product['category_id'], product_id)
    in_wishlist = False
    if 'user_id' in session:
        in_wishlist = is_in_wishlist(session['user_id'], product_id)

    # Track recently viewed in session (max 6)
    viewed = session.get('recently_viewed', [])
    if product_id in viewed:
        viewed.remove(product_id)
    viewed.insert(0, product_id)
    session['recently_viewed'] = viewed[:6]

    # Fetch color variants for this product
    _conn = get_db()
    variants = _conn.execute(
        """SELECT id, color_name, color_hex, image_url, stock
           FROM product_variants
           WHERE product_id = ?
           ORDER BY id""",
        (product_id,)
    ).fetchall()
    _conn.close()
    variants = [dict(v) for v in variants]

    return render_template(
        'store/product_detail.html',
        product=product,
        variants=variants,
        related=related,
        in_wishlist=in_wishlist,
        cart_count=_cart_count()
    )


@store_bp.route('/category/<slug>')
def category(slug):
    """Render a category product listing with filters."""
    cat = get_category_by_slug(slug)
    if not cat:
        return render_template('404.html'), 404

    sort       = request.args.get('sort', 'newest')
    min_price  = request.args.get('min_price', type=float)
    max_price  = request.args.get('max_price', type=float)
    min_rating = request.args.get('min_rating', type=float)

    products   = get_products_by_category(
        cat['id'], sort=sort,
        min_price=min_price, max_price=max_price, min_rating=min_rating
    )
    categories = get_all_categories()

    return render_template(
        'store/category.html',
        category=cat,
        products=products,
        categories=categories,
        sort=sort,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        cart_count=_cart_count()
    )


@store_bp.route('/search')
def search():
    """Handle product search requests."""
    query = request.args.get('q', '').strip()
    sort  = request.args.get('sort', 'newest')
    min_price  = request.args.get('min_price', type=float)
    max_price  = request.args.get('max_price', type=float)
    min_rating = request.args.get('min_rating', type=float)

    products = []
    if query:
        products = search_products(query, limit=50)
        # Apply extra filters client-side (already limited server-side)

    categories = get_all_categories()
    return render_template(
        'store/search_results.html',
        query=query,
        products=products,
        categories=categories,
        sort=sort,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        cart_count=_cart_count()
    )


@store_bp.route('/api/search')
def api_search():
    """JSON API endpoint for live search dropdown."""
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])
    products = search_products(query, limit=6)
    results = [
        {
            'id':        p['id'],
            'name':      p['name'],
            'price':     p['price'],
            'image_url': p['image_url'],
            'category':  p['category_name'],
        }
        for p in products
    ]
    return jsonify(results)
