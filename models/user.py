"""
user.py - User model: CRUD operations for the users table.
"""
from .database import get_db
from werkzeug.security import generate_password_hash, check_password_hash


def get_user_by_email(email):
    """Fetch a user row by email address."""
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    """Fetch a user row by primary key."""
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return user


def create_user(name, email, password):
    """Insert a new user and return the new row id, or None on duplicate email."""
    password_hash = generate_password_hash(password)
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        conn.commit()
        new_id = cursor.lastrowid
    except Exception:
        new_id = None
    finally:
        conn.close()
    return new_id


def verify_password(user, password):
    """Return True if password matches the stored hash."""
    return check_password_hash(user['password_hash'], password)


def update_user(user_id, name, email, avatar=None):
    """Update user profile fields."""
    conn = get_db()
    if avatar:
        conn.execute(
            "UPDATE users SET name=?, email=?, avatar=? WHERE id=?",
            (name, email, avatar, user_id)
        )
    else:
        conn.execute(
            "UPDATE users SET name=?, email=? WHERE id=?",
            (name, email, user_id)
        )
    conn.commit()
    conn.close()


def update_password(user_id, new_password):
    """Hash and store a new password."""
    conn = get_db()
    conn.execute(
        "UPDATE users SET password_hash=? WHERE id=?",
        (generate_password_hash(new_password), user_id)
    )
    conn.commit()
    conn.close()


def get_all_users():
    """Return all users (admin use)."""
    conn = get_db()
    users = conn.execute(
        "SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return users


def get_user_wishlist(user_id):
    """Return all wishlist products for a user."""
    conn = get_db()
    items = conn.execute(
        """SELECT p.* FROM wishlist w
           JOIN products p ON w.product_id = p.id
           WHERE w.user_id = ?""",
        (user_id,)
    ).fetchall()
    conn.close()
    return items


def toggle_wishlist(user_id, product_id):
    """Add or remove a product from the user's wishlist. Returns 'added' or 'removed'."""
    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM wishlist WHERE user_id=? AND product_id=?",
        (user_id, product_id)
    ).fetchone()
    if existing:
        conn.execute(
            "DELETE FROM wishlist WHERE user_id=? AND product_id=?",
            (user_id, product_id)
        )
        action = 'removed'
    else:
        conn.execute(
            "INSERT INTO wishlist (user_id, product_id) VALUES (?, ?)",
            (user_id, product_id)
        )
        action = 'added'
    conn.commit()
    conn.close()
    return action


def is_in_wishlist(user_id, product_id):
    """Check if a product is in the user's wishlist."""
    conn = get_db()
    result = conn.execute(
        "SELECT id FROM wishlist WHERE user_id=? AND product_id=?",
        (user_id, product_id)
    ).fetchone()
    conn.close()
    return result is not None
