"""
product.py - Product model: queries for products and categories.
"""
from .database import get_db


def get_all_categories():
    """Return all categories."""
    conn = get_db()
    cats = conn.execute("SELECT * FROM categories ORDER BY id").fetchall()
    conn.close()
    return cats


def get_category_by_slug(slug):
    """Return a category row by its URL slug."""
    conn = get_db()
    cat = conn.execute(
        "SELECT * FROM categories WHERE slug=?", (slug,)
    ).fetchone()
    conn.close()
    return cat


def get_all_products(sort='newest', category_id=None,
                     min_price=None, max_price=None, min_rating=None):
    """Return products with optional filtering and sorting."""
    conn = get_db()
    query = "SELECT p.*, c.name AS category_name FROM products p JOIN categories c ON p.category_id = c.id WHERE 1=1"
    params = []

    if category_id:
        query += " AND p.category_id = ?"
        params.append(category_id)
    if min_price is not None:
        query += " AND p.price >= ?"
        params.append(min_price)
    if max_price is not None:
        query += " AND p.price <= ?"
        params.append(max_price)
    if min_rating is not None:
        query += " AND p.rating >= ?"
        params.append(min_rating)

    sort_map = {
        'newest': 'p.id DESC',
        'price_asc': 'p.price ASC',
        'price_desc': 'p.price DESC',
        'rating': 'p.rating DESC',
    }
    query += f" ORDER BY {sort_map.get(sort, 'p.id DESC')}"

    products = conn.execute(query, params).fetchall()
    conn.close()
    return products


def get_product_by_id(product_id):
    """Return a single product with its category name."""
    conn = get_db()
    product = conn.execute(
        """SELECT p.*, c.name AS category_name, c.slug AS category_slug
           FROM products p JOIN categories c ON p.category_id = c.id
           WHERE p.id = ?""",
        (product_id,)
    ).fetchone()
    conn.close()
    return product


def get_featured_products(limit=8):
    """Return products marked as featured."""
    conn = get_db()
    products = conn.execute(
        """SELECT p.*, c.name AS category_name FROM products p
           JOIN categories c ON p.category_id = c.id
           WHERE p.is_featured = 1 ORDER BY p.rating DESC LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return products


def get_todays_deals(limit=6):
    """Return products marked as today's deals."""
    conn = get_db()
    products = conn.execute(
        """SELECT p.*, c.name AS category_name FROM products p
           JOIN categories c ON p.category_id = c.id
           WHERE p.is_deal = 1 ORDER BY p.rating DESC LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return products


def get_best_sellers(limit=10):
    """Return top products by review count (proxy for sales)."""
    conn = get_db()
    products = conn.execute(
        """SELECT p.*, c.name AS category_name FROM products p
           JOIN categories c ON p.category_id = c.id
           ORDER BY p.reviews_count DESC LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return products


def get_products_by_category(category_id, limit=None, sort='newest',
                              min_price=None, max_price=None, min_rating=None):
    """Return products in a given category with optional filters."""
    return get_all_products(sort=sort, category_id=category_id,
                            min_price=min_price, max_price=max_price,
                            min_rating=min_rating)


def search_products(query, limit=20):
    """Full-text-style search across product name and description."""
    conn = get_db()
    like = f"%{query}%"
    products = conn.execute(
        """SELECT p.*, c.name AS category_name FROM products p
           JOIN categories c ON p.category_id = c.id
           WHERE p.name LIKE ? OR p.description LIKE ?
           ORDER BY p.rating DESC LIMIT ?""",
        (like, like, limit)
    ).fetchall()
    conn.close()
    return products


def get_related_products(category_id, exclude_id, limit=4):
    """Return products in the same category, excluding the current product."""
    conn = get_db()
    products = conn.execute(
        """SELECT p.*, c.name AS category_name FROM products p
           JOIN categories c ON p.category_id = c.id
           WHERE p.category_id = ? AND p.id != ?
           ORDER BY p.rating DESC LIMIT ?""",
        (category_id, exclude_id, limit)
    ).fetchall()
    conn.close()
    return products


# ── Admin CRUD ────────────────────────────────────────────────────────────────

def add_product(name, description, price, old_price, category_id,
                image_url, stock, is_featured=0, is_deal=0):
    """Insert a new product and return its id."""
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO products
           (name, description, price, old_price, category_id,
            image_url, stock, is_featured, is_deal)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, description, price, old_price, category_id,
         image_url, stock, is_featured, is_deal)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def update_product(product_id, name, description, price, old_price,
                   category_id, image_url, stock, is_featured, is_deal):
    """Update an existing product."""
    conn = get_db()
    conn.execute(
        """UPDATE products SET name=?, description=?, price=?, old_price=?,
           category_id=?, image_url=?, stock=?, is_featured=?, is_deal=?
           WHERE id=?""",
        (name, description, price, old_price, category_id, image_url,
         stock, is_featured, is_deal, product_id)
    )
    conn.commit()
    conn.close()


def delete_product(product_id):
    """Delete a product by id."""
    conn = get_db()
    conn.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()


def update_stock(product_id, quantity_sold):
    """Decrement product stock after purchase."""
    conn = get_db()
    conn.execute(
        "UPDATE products SET stock = MAX(0, stock - ?) WHERE id=?",
        (quantity_sold, product_id)
    )
    conn.commit()
    conn.close()


def get_product_variants(product_id):
    """Return all variants for a given product."""
    conn = get_db()
    variants = conn.execute(
        "SELECT * FROM product_variants WHERE product_id = ?", (product_id,)
    ).fetchall()
    conn.close()
    return variants


def get_variant_by_id(variant_id):
    """Return a single variant row."""
    conn = get_db()
    variant = conn.execute(
        "SELECT * FROM product_variants WHERE id = ?", (variant_id,)
    ).fetchone()
    conn.close()
    return variant


def get_product_count():
    """Return total number of products."""
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    conn.close()
    return count
