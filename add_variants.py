import sqlite3
conn = sqlite3.connect('store.db')
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    color_name TEXT NOT NULL,
    color_hex TEXT NOT NULL,
    stock INTEGER DEFAULT 10
)""")

# Get product IDs by category
c.execute("SELECT id, name, category_id FROM products")
products = c.fetchall()

# Get category IDs
c.execute("SELECT id, name FROM categories")
categories = {row[1]: row[0] for row in c.fetchall()}

phone_colors = [
    ('Space Black', '#1a1a1a'),
    ('Silver', '#C0C0C0'),
    ('Gold', '#FFD700'),
    ('Deep Purple', '#4B0082'),
    ('Blue', '#0047AB'),
]

laptop_colors = [
    ('Space Gray', '#808080'),
    ('Silver', '#C0C0C0'),
    ('Midnight Black', '#0a0a0a'),
]

headphone_colors = [
    ('Black', '#000000'),
    ('White', '#FFFFFF'),
    ('Midnight Blue', '#003153'),
    ('Silver', '#C0C0C0'),
]

fashion_colors = [
    ('White', '#FFFFFF'),
    ('Black', '#000000'),
    ('Red', '#FF0000'),
    ('Blue', '#0000FF'),
    ('Pink', '#FFC0CB'),
]

gaming_colors = [
    ('Black', '#000000'),
    ('White', '#FFFFFF'),
    ('Red', '#FF0000'),
]

# Delete existing variants to avoid duplicates
c.execute("DELETE FROM variants")

for product_id, name, cat_id in products:
    if cat_id == categories.get('Phones'):
        colors = phone_colors
    elif cat_id == categories.get('Laptops'):
        colors = laptop_colors
    elif cat_id == categories.get('Headphones'):
        colors = headphone_colors
    elif cat_id == categories.get('Fashion'):
        colors = fashion_colors
    elif cat_id == categories.get('Gaming'):
        colors = gaming_colors
    else:
        continue

    for color_name, color_hex in colors:
        c.execute("""INSERT INTO variants
                    (product_id, color_name, color_hex, stock)
                    VALUES (?, ?, ?, ?)""",
                 (product_id, color_name, color_hex, 10))

conn.commit()
print("Added variants successfully!")
c.execute("SELECT COUNT(*) FROM variants")
print("Total variants: " + str(c.fetchone()[0]))
conn.close()
