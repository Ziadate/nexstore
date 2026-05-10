"""
database.py - SQLite database setup, initialization, and seeding.
Handles all DDL (table creation) and initial seed data insertion.
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

# Database file location (sibling to app.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'store.db')


def get_db():
    """Open a new database connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        -- Categories table
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            icon TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE
        );

        -- Users table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            avatar TEXT DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME DEFAULT NULL
        );

        -- Products table
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            old_price REAL DEFAULT NULL,
            category_id INTEGER NOT NULL,
            image_url TEXT,
            stock INTEGER DEFAULT 10,
            rating REAL DEFAULT 4.0,
            reviews_count INTEGER DEFAULT 0,
            is_featured INTEGER DEFAULT 0,
            is_deal INTEGER DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );

        -- Product Variants table
        CREATE TABLE IF NOT EXISTS product_variants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            color_name TEXT NOT NULL,
            color_hex TEXT NOT NULL,
            stock INTEGER NOT NULL DEFAULT 10,
            price_modifier REAL NOT NULL DEFAULT 0,
            image_url TEXT DEFAULT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );

        -- Cart table
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            variant_id INTEGER DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (variant_id) REFERENCES product_variants(id),
            UNIQUE(user_id, product_id, variant_id)
        );

        -- Wishlist table
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            UNIQUE(user_id, product_id)
        );

        -- Orders table
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_price REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            payment_method TEXT NOT NULL DEFAULT 'cod',
            address TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        -- Order Items table
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            variant_id INTEGER DEFAULT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id),
            FOREIGN KEY (variant_id) REFERENCES product_variants(id)
        );

        -- Admin Sessions table
        CREATE TABLE IF NOT EXISTS admin_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_email TEXT NOT NULL,
            session_token TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()


def seed_db():
    """Insert sample data only if the tables are empty."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return  # Already seeded

    # ── Categories ────────────────────────────────────────────────────────────
    categories = [
        ('Phones',           '📱', 'phones'),
        ('Headphones',       '🎧', 'headphones'),
        ('Laptops',          '💻', 'laptops'),
        ('Fashion',          '👗', 'fashion'),
        ('Home Appliances',  '🏠', 'home-appliances'),
        ('Gaming',           '🎮', 'gaming'),
    ]
    cursor.executemany(
        "INSERT INTO categories (name, icon, slug) VALUES (?, ?, ?)", categories
    )

    # ── Users ─────────────────────────────────────────────────────────────────
    users = [
        ('Admin User',  'admin@store.com', generate_password_hash('admin123'), 'admin'),
        ('Test User',   'user@store.com',  generate_password_hash('user123'),  'user'),
    ]
    cursor.executemany(
        "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)", users
    )

    # ── Products ──────────────────────────────────────────────────────────────
    products = [
        # Phones (cat 1)
        ('Samsung Galaxy S24 Ultra', 'The ultimate Samsung flagship with AI-powered camera and titanium frame.', 1199.99, 1399.99, 1, 'https://images.unsplash.com/photo-1707065090130-f80e920d393f?auto=format&fit=crop&w=600&h=600&q=80', 15, 4.8, 2341, 1, 0),
        ('iPhone 15 Pro Max', 'Apple\'s most powerful iPhone with A17 Pro chip and titanium design.', 1299.99, 1499.99, 1, 'https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=600&h=600&q=80', 10, 4.9, 5120, 1, 1),
        ('Google Pixel 8', 'Pure Android experience with Google\'s best AI camera features.', 699.99, 799.99, 1, 'https://images.unsplash.com/photo-1696429175928-793a1cdef1d3?auto=format&fit=crop&w=600&h=600&q=80', 20, 4.6, 987, 0, 0),
        ('OnePlus 12', 'Flagship killer with Snapdragon 8 Gen 3 and 100W fast charging.', 799.99, 899.99, 1, 'https://images.unsplash.com/photo-1612444530582-fc66183b16f7?auto=format&fit=crop&w=600&h=600&q=80', 18, 4.7, 1243, 0, 1),
        ('Xiaomi 14 Pro', 'Leica-powered cameras and top-tier performance at a great price.', 649.99, 749.99, 1, 'https://images.unsplash.com/photo-1556656793-062ff98782ee?auto=format&fit=crop&w=600&h=600&q=80', 25, 4.5, 876, 0, 0),

        # Headphones (cat 2)
        ('Sony WH-1000XM5', 'Industry-leading noise cancellation with 30-hour battery life.', 349.99, 399.99, 2, 'https://images.unsplash.com/photo-1675243935987-399b0f5dd4af?auto=format&fit=crop&w=600&h=600&q=80', 30, 4.9, 8760, 1, 0),
        ('Apple AirPods Pro 2', 'Adaptive Transparency, Personalized Spatial Audio and H2 chip.', 249.99, 279.99, 2, 'https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400', 40, 4.8, 12430, 1, 1),
        ('Bose QuietComfort 45', 'Legendary Bose comfort with world-class noise cancellation.', 279.99, 329.99, 2, 'https://images.unsplash.com/photo-1613040809024-b4ef7ba99bc3?auto=format&fit=crop&w=600&h=600&q=80', 22, 4.7, 4320, 0, 0),
        ('Sennheiser HD 660S', 'Reference open-back headphones for audiophiles.', 499.99, 599.99, 2, 'https://images.unsplash.com/photo-1615655406736-b37c4fabf923?auto=format&fit=crop&w=600&h=600&q=80', 8, 4.8, 1230, 0, 0),
        ('JBL Live 770NC', 'Adaptive noise cancelling with immersive JBL sound.', 149.99, 199.99, 2, 'https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?auto=format&fit=crop&w=600&h=600&q=80', 35, 4.4, 3210, 0, 1),

        # Laptops (cat 3)
        ('MacBook Pro 16" M3 Max', 'The most powerful MacBook ever with M3 Max chip and 22-hour battery.', 2499.99, 2799.99, 3, 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=600&h=600&q=80', 12, 4.9, 3450, 1, 0),
        ('Dell XPS 15', 'Premium Windows laptop with OLED display and Intel Core Ultra.', 1799.99, 1999.99, 3, 'https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?auto=format&fit=crop&w=600&h=600&q=80', 14, 4.7, 2100, 1, 0),
        ('ASUS ROG Zephyrus G14', 'Gaming powerhouse with AMD Ryzen 9 and RTX 4060.', 1499.99, 1699.99, 3, 'https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=600&h=600&q=80', 9, 4.6, 1567, 0, 1),
        ('Lenovo ThinkPad X1 Carbon', 'Business ultrabook with legendary ThinkPad reliability.', 1399.99, 1599.99, 3, 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=600&h=600&q=80', 16, 4.7, 2890, 0, 0),
        ('Microsoft Surface Laptop 5', 'Elegant design with vibrant PixelSense touchscreen display.', 1299.99, 1499.99, 3, 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400', 11, 4.5, 1234, 0, 0),

        # Fashion (cat 4)
        ('Nike Air Max 270', 'Iconic Max Air unit with modern streetwear aesthetic.', 149.99, 179.99, 4, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&h=600&q=80', 50, 4.6, 5670, 1, 0),
        ('Adidas Ultraboost 23', 'The ultimate running shoe with responsive Boost cushioning.', 179.99, 219.99, 4, 'https://images.unsplash.com/photo-1608231387042-66d1773070a5?auto=format&fit=crop&w=600&h=600&q=80', 45, 4.7, 4320, 0, 1),
        ('Levi\'s 501 Original Jeans', 'The original and most iconic jeans in history.', 79.99, 99.99, 4, 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=600&h=600&q=80', 80, 4.5, 9870, 0, 0),
        ('Ray-Ban Aviator Classic', 'Timeless aviator sunglasses with glass lenses.', 199.99, 249.99, 4, 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?auto=format&fit=crop&w=600&h=600&q=80', 60, 4.8, 7650, 1, 0),
        ('The North Face Puffer Jacket', 'Warm, lightweight 550-fill down jacket for cold adventures.', 249.99, 299.99, 4, 'https://images.unsplash.com/photo-1606521467890-24e4f4b4a0d5?auto=format&fit=crop&w=600&h=600&q=80', 30, 4.7, 3210, 0, 0),

        # Home Appliances (cat 5)
        ('Dyson V15 Detect', 'Laser Detect technology reveals hidden dust with powerful suction.', 699.99, 799.99, 5, 'https://images.unsplash.com/photo-1558317374-067fb5f30001?auto=format&fit=crop&w=600&h=600&q=80', 20, 4.8, 4560, 1, 0),
        ('Instant Pot Duo 7-in-1', 'Multi-use pressure cooker that replaces 7 kitchen appliances.', 99.99, 129.99, 5, 'https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=600&h=600&q=80', 55, 4.7, 23456, 1, 1),
        ('Nespresso Vertuo Next', 'Revolutionary coffee machine with centrifusion technology.', 179.99, 229.99, 5, 'https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?auto=format&fit=crop&w=600&h=600&q=80', 35, 4.5, 8900, 0, 0),
        ('iRobot Roomba i7+', 'Self-emptying robot vacuum with smart mapping technology.', 599.99, 699.99, 5, 'https://images.unsplash.com/photo-1621360841013-c7683c659ec6?auto=format&fit=crop&w=600&h=600&q=80', 18, 4.6, 5670, 0, 0),
        ('Philips Hue Starter Kit', 'Smart LED bulbs with 16 million colors and voice control.', 129.99, 179.99, 5, 'https://images.unsplash.com/photo-1550524514-963d0cc190a2?auto=format&fit=crop&w=600&h=600&q=80', 40, 4.4, 3456, 0, 1),

        # Gaming (cat 6)
        ('PlayStation 5', 'Sony\'s next-gen console with lightning-fast SSD and DualSense controller.', 499.99, 549.99, 6, 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=600&h=600&q=80', 5, 4.9, 15670, 1, 0),
        ('Xbox Series X', 'Microsoft\'s most powerful Xbox ever with 12 teraflops of performance.', 499.99, 549.99, 6, 'https://images.unsplash.com/photo-1621259182978-f09e5e2ca1ff?auto=format&fit=crop&w=600&h=600&q=80', 7, 4.8, 9870, 1, 0),
        ('Nintendo Switch OLED', 'Enhanced gaming with vibrant 7-inch OLED screen.', 349.99, 399.99, 6, 'https://images.unsplash.com/photo-1578303318323-26421b21ef1c?auto=format&fit=crop&w=600&h=600&q=80', 20, 4.8, 12340, 0, 1),
        ('Razer DeathAdder V3', 'Iconic ergonomic gaming mouse with Focus Pro 30K sensor.', 99.99, 129.99, 6, 'https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=600&h=600&q=80', 45, 4.7, 5670, 0, 0),
        ('SteelSeries Apex Pro', 'The world\'s fastest mechanical keyboard with adjustable actuation.', 199.99, 249.99, 6, 'https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=600&h=600&q=80', 28, 4.8, 4320, 0, 0),
        ('LG UltraGear 27" 4K', '27" 4K IPS gaming monitor with 144Hz and 1ms response time.', 599.99, 699.99, 6, 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=600&h=600&q=80', 12, 4.7, 2340, 1, 1),
    ]
    cursor.executemany(
        """INSERT INTO products
           (name, description, price, old_price, category_id, image_url,
            stock, rating, reviews_count, is_featured, is_deal)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        products
    )
    conn.commit()
    conn.close()
    print("Database seeded successfully!")