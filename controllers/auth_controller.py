"""
auth_controller.py - Handles user login, registration, and logout.
Blueprint: 'auth', URL prefix: /auth
"""
from urllib.parse import urlparse
from flask import (Blueprint, render_template, redirect, url_for,
                   request, session, flash, jsonify)
from models.user import get_user_by_email, create_user, verify_password

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def _safe_next(url):
    """Ensure redirects after login are safe and intentional."""
    if not url:
        return url_for('store.home')
    parsed = urlparse(url)
    # Reject redirects to external domains
    if parsed.netloc and parsed.netloc != request.host:
        return url_for('store.home')

    # Block action URLs to prevent unintended behavior like auto-add-to-cart after login
    if '/cart/add' in parsed.path or '/checkout' in parsed.path:
        return url_for('store.home')

    # Allow redirects to the profile page
    if parsed.path.startswith('/profile'):
        return url

    # Default to home for everything else
    return url_for('store.home')


def login_required(f):
    """Decorator to require login for protected routes."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Decorator to require admin role."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('store.home'))
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Display login form and handle submission."""
    if 'user_id' in session:
        return redirect(url_for('store.home'))

    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = request.form.get('remember')

        user = get_user_by_email(email)
        if user and verify_password(user, password):
            session.permanent = bool(remember)
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            session['role']      = user['role']
            flash(f'Welcome back, {user["name"]}! 👋', 'success')
            next_page = _safe_next(request.args.get('next'))
            return redirect(next_page)
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Display registration form and handle submission."""
    if 'user_id' in session:
        return redirect(url_for('store.home'))

    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        # Basic server-side validation
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
        elif password != confirm:
            flash('Passwords do not match.', 'danger')
        else:
            new_id = create_user(name, email, password)
            if new_id:
                # Auto-login: populate session just like login does
                user = get_user_by_email(email)
                if user:
                    session.permanent = False
                    session['user_id']   = user['id']
                    session['user_name'] = user['name']
                    session['role']      = user['role']
                    flash(f'Welcome to NexStore, {name}! 🎉 Your account has been created.', 'success')
                    return redirect(url_for('store.home'))
                else:
                    flash('Account created, but automatic login failed. Please log in manually.', 'warning')
                    return redirect(url_for('auth.login'))
            else:
                flash('Email already in use. Please try another.', 'danger')

    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """Clear session and redirect to login."""
    name = session.get('user_name', 'User')
    session.clear()
    flash(f'Goodbye, {name}! See you soon. 👋', 'info')
    return redirect(url_for('store.home'))
