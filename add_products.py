"""
add_products.py — One-shot script to insert 20+ new products into store.db.
Skips any product whose name already exists to prevent duplicates.
Run from the online_store/ directory: python add_products.py
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'store.db')

# (name, description, price, old_price, cat_id, image_url, stock, rating, reviews, featured, deal)
# Categories: 1=Phones, 2=Headphones, 3=Laptops, 4=Fashion, 5=Home Appliances, 6=Gaming
NEW_PRODUCTS = [
    # ── Phones (cat 1) ──────────────────────────────────────────────────────
    ('Google Pixel 9 Pro',
     'Google\'s latest flagship with Gemini AI, advanced Pro camera system and stunning design.',
     999.99, 1099.99, 1,
     'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400',
     20, 4.9, 150, 1, 0),

    ('OnePlus 12',
     'The pinnacle of performance with Snapdragon 8 Gen 3 and Hasselblad Camera.',
     799.99, 899.99, 1,
     'https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=400',
     15, 4.8, 230, 0, 1),

    ('Xiaomi 14 Ultra',
     'Leica professional optics and 1-inch main sensor for ultimate mobile photography.',
     699.99, 799.99, 1,
     'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400',
     10, 4.7, 180, 0, 0),

    # ── Gaming (cat 6) ──────────────────────────────────────────────────────
    ('Xbox Series X',
     'The fastest, most powerful Xbox ever. Play thousands of titles from four generations.',
     499.99, 549.99, 6,
     'https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=400',
     12, 4.9, 850, 1, 0),

    ('Nintendo Switch OLED',
     'Features a vibrant 7-inch OLED screen, a wide adjustable stand, and more.',
     349.99, 399.99, 6,
     'https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=400',
     25, 4.8, 1200, 0, 1),

    ('Gaming Headset Pro',
     'Immersive surround sound and crystal-clear microphone for competitive gaming.',
     199.99, 249.99, 6,
     'https://images.unsplash.com/photo-1599669454699-248893623440?w=400',
     30, 4.6, 450, 0, 0),

    # ── Fashion (cat 4) ─────────────────────────────────────────────────────
    ('Nike Air Max 2024',
     'Revolutionary Air unit for all-day comfort and futuristic style.',
     189.99, 219.99, 4,
     'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400',
     40, 4.7, 320, 1, 0),

    ('Adidas Ultraboost',
     'Iconic energy return with every step. The ultimate running experience.',
     179.99, 199.99, 4,
     'https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400',
     35, 4.7, 280, 0, 1),

    ('Leather Watch Classic',
     'Timeless elegance with a premium leather strap and precision movement.',
     299.99, 349.99, 4,
     'https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=400',
     20, 4.8, 120, 0, 0),

    # ── Home Appliances (cat 5) ─────────────────────────────────────────────
    ('Nespresso Machine',
     'High-pressure pump and perfect heat control for barista-quality coffee.',
     299.99, 349.99, 5,
     'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400',
     18, 4.6, 540, 0, 1),

    ('Air Purifier Pro',
     'Advanced HEPA filtration system captures 99.97% of airborne particles.',
     399.99, 449.99, 5,
     'https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400',
     15, 4.8, 190, 1, 0),

    ('Smart Blender',
     'High-speed motor and smart presets for the perfect smoothie every time.',
     149.99, 189.99, 5,
     'https://images.unsplash.com/photo-1570222094114-d054a817e56b?w=400',
     22, 4.5, 310, 0, 0),
]


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    added = 0
    skipped = 0

    for product in NEW_PRODUCTS:
        name = product[0]
        existing = conn.execute(
            "SELECT id FROM products WHERE name = ?", (name,)
        ).fetchone()
        if existing:
            print(f"  SKIP (exists): {name}")
            skipped += 1
            continue

        conn.execute(
            """INSERT INTO products
               (name, description, price, old_price, category_id, image_url,
                stock, rating, reviews_count, is_featured, is_deal)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            product
        )
        print(f"  ADDED: {name}")
        added += 1

    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    conn.close()
    print(f"\nDone! Added {added}, skipped {skipped}. Total products in DB: {total}")


if __name__ == '__main__':
    main()
