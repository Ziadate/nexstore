"""
migrate_variants.py - Creates product_variants table and seeds color data.
Safe to run multiple times (skips existing variants per product).
Run: python migrate_variants.py
"""
import sqlite3

DB_PATH = 'store.db'

# ── Real Unsplash image URLs per color ────────────────────────────────────────
PHONE_VARIANTS = [
    ('Midnight Black', '#1C1C1C',
     'https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&q=80', 15),
    ('Starlight',      '#F2F2F2',
     'https://images.unsplash.com/photo-1556656793-08538906a9f8?w=800&q=80', 12),
    ('Blue',           '#2B4B8C',
     'https://images.unsplash.com/photo-1574944985070-8f3ebc6b79d2?w=800&q=80', 10),
    ('Red',            '#B22222',
     'https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=800&q=80',  8),
]

LAPTOP_VARIANTS = [
    ('Silver',     '#C0C0C0',
     'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80', 10),
    ('Space Gray', '#4A4A4A',
     'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80',  8),
    ('Gold',       '#C9A84C',
     'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=800&q=80',    5),
    ('White',      '#F5F5F5',
     'https://images.unsplash.com/photo-1611186871525-b6f6c946e0e0?w=800&q=80',  6),
]

HEADPHONE_VARIANTS = [
    ('Black',        '#111111',
     'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80', 20),
    ('White',        '#EFEFEF',
     'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=800&q=80', 15),
    ('Midnight Blue','#003153',
     'https://images.unsplash.com/photo-1484704849700-f032a568e944?w=800&q=80', 10),
    ('Silver',       '#C0C0C0',
     'https://images.unsplash.com/photo-1487215078519-e21cc028cb29?w=800&q=80', 12),
]


def run():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # ── 1. Create table ────────────────────────────────────────────────────────
    c.execute("""
        CREATE TABLE IF NOT EXISTS product_variants (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            color_name TEXT    NOT NULL,
            color_hex  TEXT    NOT NULL,
            image_url  TEXT,
            stock      INTEGER DEFAULT 0,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    """)
    conn.commit()
    print("Table product_variants ready.")

    # ── 2. Resolve categories ──────────────────────────────────────────────────
    cats = {row['name']: row['id']
            for row in c.execute("SELECT id, name FROM categories").fetchall()}

    # ── 3. Seed function (idempotent) ──────────────────────────────────────────
    total_added = 0

    def seed(category_name, variants, limit=3):
        nonlocal total_added
        cat_id = cats.get(category_name)
        if not cat_id:
            print(f"  Category not found: {category_name!r}")
            return
        products = c.execute(
            "SELECT id, name FROM products WHERE category_id=? LIMIT ?",
            (cat_id, limit)
        ).fetchall()

        for prod in products:
            pid = prod['id']
            # Skip products that already have variants
            existing = c.execute(
                "SELECT COUNT(*) FROM product_variants WHERE product_id=?", (pid,)
            ).fetchone()[0]
            if existing:
                print(f"  SKIP '{prod['name']}' (already has {existing} variants)")
                continue

            for color_name, color_hex, image_url, stock in variants:
                c.execute(
                    """INSERT INTO product_variants
                       (product_id, color_name, color_hex, image_url, stock)
                       VALUES (?,?,?,?,?)""",
                    (pid, color_name, color_hex, image_url, stock)
                )
                total_added += 1
            print(f"  ADDED {len(variants)} variants for '{prod['name']}'")

    # ── 4. Seed categories ─────────────────────────────────────────────────────
    print("\nSeeding Phones...")
    seed('Phones',     PHONE_VARIANTS,     limit=4)

    print("Seeding Laptops...")
    seed('Laptops',    LAPTOP_VARIANTS,    limit=4)

    print("Seeding Headphones...")
    seed('Headphones', HEADPHONE_VARIANTS, limit=2)

    conn.commit()

    # ── 5. Summary ─────────────────────────────────────────────────────────────
    total = c.execute("SELECT COUNT(*) FROM product_variants").fetchone()[0]
    products_with = c.execute(
        "SELECT COUNT(DISTINCT product_id) FROM product_variants"
    ).fetchone()[0]
    print(f"\nDone! Added {total_added} new variant rows.")
    print(f"Total in DB: {total} variants across {products_with} products.")
    conn.close()


if __name__ == '__main__':
    run()
