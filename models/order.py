"""
order.py - Order model: create and query orders and order items.
"""
from .database import get_db


def create_order(user_id, total_price, payment_method, address):
    """Insert a new order record and return its id."""
    conn = get_db()
    cursor = conn.execute(
        """INSERT INTO orders (user_id, total_price, payment_method, address)
           VALUES (?, ?, ?, ?)""",
        (user_id, total_price, payment_method, address)
    )
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return order_id


def create_order_items(order_id, items):
    """
    Bulk-insert order line items.
    items: list of (product_id, quantity, price) tuples.
    """
    conn = get_db()
    conn.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
        [(order_id, item['product_id'], item['quantity'], item['price']) for item in items]
    )
    conn.commit()
    conn.close()


def get_order_by_id(order_id):
    """Return a single order with its items and product details."""
    conn = get_db()
    order = conn.execute(
        """SELECT o.*, u.name AS user_name, u.email AS user_email
           FROM orders o JOIN users u ON o.user_id = u.id
           WHERE o.id = ?""",
        (order_id,)
    ).fetchone()
    if order:
        items = conn.execute(
            """SELECT oi.*, p.name AS product_name, p.image_url
               FROM order_items oi JOIN products p ON oi.product_id = p.id
               WHERE oi.order_id = ?""",
            (order_id,)
        ).fetchall()
    else:
        items = []
    conn.close()
    return order, items


def get_user_orders(user_id):
    """Return all orders for a user, newest first."""
    conn = get_db()
    orders = conn.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return orders


def get_all_orders(limit=50):
    """Return recent orders with user info (admin use)."""
    conn = get_db()
    orders = conn.execute(
        """SELECT o.*, u.name AS user_name, u.email AS user_email
           FROM orders o JOIN users u ON o.user_id = u.id
           ORDER BY o.created_at DESC LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return orders


def update_order_status(order_id, status):
    """Update the status of an order (pending, processing, shipped, delivered, cancelled)."""
    conn = get_db()
    conn.execute(
        "UPDATE orders SET status=? WHERE id=?", (status, order_id)
    )
    conn.commit()
    conn.close()


def get_total_revenue():
    """Return total revenue from all delivered orders."""
    conn = get_db()
    result = conn.execute(
        "SELECT COALESCE(SUM(total_price), 0) FROM orders WHERE status != 'cancelled'"
    ).fetchone()[0]
    conn.close()
    return round(result, 2)


def get_order_count():
    conn = get_db()
    count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    conn.close()
    return count


def get_orders_by_category():
    """Return order counts grouped by category name."""
    conn = get_db()
    results = conn.execute("""
        SELECT c.name, COUNT(oi.id) as count
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id
        LEFT JOIN order_items oi ON p.id = oi.product_id
        GROUP BY c.id
    """).fetchall()
    conn.close()
    return results


def get_orders_by_payment_method():
    """Return order counts grouped by payment method."""
    conn = get_db()
    results = conn.execute("""
        SELECT payment_method, COUNT(*) as count
        FROM orders
        GROUP BY payment_method
    """).fetchall()
    conn.close()
    return results


def get_revenue_trend(days=7):
    """Return daily revenue for the last N days."""
    conn = get_db()
    results = conn.execute(f"""
        SELECT date(created_at) as day, SUM(total_price) as revenue
        FROM orders
        WHERE created_at >= date('now', '-{days} days')
        AND status != 'cancelled'
        GROUP BY day
        ORDER BY day ASC
    """).fetchall()
    conn.close()
    return results
