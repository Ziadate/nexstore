"""
cart.py - Cart model: manage items in the user's cart.
"""
from .database import get_db


def get_cart_items(user_id):
    """Return all cart items with product and variant details."""
    conn = get_db()
    items = conn.execute(
        """SELECT c.id, c.quantity, p.id AS product_id, p.name, p.price,
                  p.old_price, p.image_url, p.stock,
                  v.color_name, v.color_hex, v.price_modifier
           FROM cart c
           JOIN products p ON c.product_id = p.id
           LEFT JOIN product_variants v ON c.variant_id = v.id
           WHERE c.user_id = ?
           ORDER BY c.id DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    return items


def get_cart_count(user_id):
    """Return total number of distinct items in the cart."""
    conn = get_db()
    result = conn.execute(
        "SELECT COUNT(*) FROM cart WHERE user_id=?", (user_id,)
    ).fetchone()[0]
    conn.close()
    return result


def add_to_cart(user_id, product_id, quantity=1, variant_id=None):
    """Add product to cart; distinguish by variant_id."""
    conn = get_db()
    existing = conn.execute(
        "SELECT id, quantity FROM cart WHERE user_id=? AND product_id=? AND (variant_id=? OR (variant_id IS NULL AND ? IS NULL))",
        (user_id, product_id, variant_id, variant_id)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE cart SET quantity = quantity + ? WHERE id=?",
            (quantity, existing['id'])
        )
    else:
        conn.execute(
            "INSERT INTO cart (user_id, product_id, quantity, variant_id) VALUES (?, ?, ?, ?)",
            (user_id, product_id, quantity, variant_id)
        )
    conn.commit()
    conn.close()


def update_quantity(user_id, product_id, quantity):
    """Set the quantity of a cart item; remove if quantity ≤ 0."""
    conn = get_db()
    if quantity <= 0:
        conn.execute(
            "DELETE FROM cart WHERE user_id=? AND product_id=?",
            (user_id, product_id)
        )
    else:
        conn.execute(
            "UPDATE cart SET quantity=? WHERE user_id=? AND product_id=?",
            (quantity, user_id, product_id)
        )
    conn.commit()
    conn.close()


def remove_from_cart(user_id, product_id):
    """Remove a specific item from the cart."""
    conn = get_db()
    conn.execute(
        "DELETE FROM cart WHERE user_id=? AND product_id=?",
        (user_id, product_id)
    )
    conn.commit()
    conn.close()


def clear_cart(user_id):
    """Remove all items from a user's cart."""
    conn = get_db()
    conn.execute("DELETE FROM cart WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


def get_cart_total(user_id):
    """Return subtotal including variant price modifiers."""
    conn = get_db()
    result = conn.execute(
        """SELECT COALESCE(SUM((p.price + COALESCE(v.price_modifier, 0)) * c.quantity), 0)
           FROM cart c 
           JOIN products p ON c.product_id = p.id
           LEFT JOIN product_variants v ON c.variant_id = v.id
           WHERE c.user_id = ?""",
        (user_id,)
    ).fetchone()[0]
    conn.close()
    return round(result, 2)
