"""
seed_variants.py - Seeds color variants for all applicable product categories.
Run once: python seed_variants.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'store.db')

PHONE_COLORS     = [('#1c1c1c','Space Black',20,0),('#e3e4e5','Silver',15,0),
                    ('#f5e1c0','Gold',10,50),('#4b0082','Deep Purple',12,0),('#215e7c','Blue',14,0)]
LAPTOP_COLORS    = [('#5e5e5e','Space Gray',10,0),('#e3e4e5','Silver',8,0),
                    ('#1a1a1a','Midnight Black',6,100)]
HEADPHONE_COLORS = [('#1a1a1a','Black',30,0),('#ffffff','White',20,0),
                    ('#1a3a5c','Midnight Blue',12,20),('#c0c0c0','Silver',15,0)]
FASHION_COLORS   = [('#ffffff','White',40,0),('#1a1a1a','Black',35,0),
                    ('#c0392b','Red',25,0),('#154360','Blue',30,0),('#d35400','Pink',20,0)]
GAMING_COLORS    = [('#1a1a1a','Black',15,0),('#ffffff','White',10,0),('#c0392b','Red',8,30)]

def seed_variants():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Clear existing variants first to avoid duplicates
    c.execute("DELETE FROM product_variants")
    conn.commit()

    # Get products by category
    cat_map = {row[0]: row[1] for row in c.execute("SELECT slug, id FROM categories").fetchall()}

    def insert_variants(cat_slug, colors):
        cat_id = cat_map.get(cat_slug)
        if not cat_id:
            print(f"Category not found: {cat_slug}")
            return
        products = c.execute("SELECT id FROM products WHERE category_id=?", (cat_id,)).fetchall()
        for (pid,) in products:
            for (hex_val, name, stock, price_mod) in colors:
                c.execute(
                    "INSERT INTO product_variants (product_id, color_name, color_hex, stock, price_modifier) VALUES (?,?,?,?,?)",
                    (pid, name, hex_val, stock, price_mod)
                )
        print(f"  {cat_slug}: inserted {len(colors)} colors × {len(products)} products")

    insert_variants('phones',      PHONE_COLORS)
    insert_variants('laptops',     LAPTOP_COLORS)
    insert_variants('headphones',  HEADPHONE_COLORS)
    insert_variants('fashion',     FASHION_COLORS)
    insert_variants('gaming',      GAMING_COLORS)

    conn.commit()
    conn.close()
    print("✅ Variants seeded successfully!")

if __name__ == '__main__':
    seed_variants()
