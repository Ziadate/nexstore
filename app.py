"""
app.py - Flask application entry point.
Registers all blueprints, initializes the database, and starts the dev server.
"""
import os
from flask import Flask, render_template
from models.database import init_db, seed_db

# ── Wishlist toggle route (lives here for simplicity) ─────────────────────
from flask import session, jsonify, request as flask_request
from models.user import toggle_wishlist


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Fixed secret key — must be consistent across restarts for sessions to work
    app.secret_key = 'nexstore-admin-secret-key-2024-fixed'
    app.config['PERMANENT_SESSION_LIFETIME'] = 60 * 60 * 24 * 30  # 30 days

    # Admin credentials — stored in app.config, read via current_app in controller
    app.config['ADMIN_EMAIL']    = 'admin@nexstore.com'
    app.config['ADMIN_PASSWORD'] = 'nexstore2024'

    # ── Register Blueprints ───────────────────────────────────────────────
    from controllers.auth_controller    import auth_bp
    from controllers.product_controller import store_bp
    from controllers.cart_controller    import cart_bp
    from controllers.order_controller   import order_bp
    from controllers.admin_controller   import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(store_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(admin_bp)

    # ── Wishlist toggle (AJAX) ────────────────────────────────────────────
    @app.route('/wishlist/toggle', methods=['POST'])
    def wishlist_toggle():
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Login required'}), 401
        product_id = flask_request.form.get('product_id', type=int)
        if not product_id:
            return jsonify({'success': False, 'message': 'Invalid product'}), 400
        action = toggle_wishlist(session['user_id'], product_id)
        return jsonify({'success': True, 'action': action})

    # ── Error Handlers ────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500

    # ── Init & Seed DB ────────────────────────────────────────────────────
    with app.app_context():
        init_db()
        seed_db()

    return app


if __name__ == '__main__':
    app = create_app()
    print("Online Store running at http://localhost:5000")
    print("   Admin Panel: http://localhost:5000/admin/login")
    print("   Admin Email: admin@nexstore.com")
    print("   Admin Pass:  nexstore2024")
    print("   User:  user@store.com  / user123")
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
