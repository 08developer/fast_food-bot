import aiosqlite

DB_PATH = "fastfood.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                emoji TEXT DEFAULT '🍽️'
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                available INTEGER DEFAULT 1,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );

            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY (product_id) REFERENCES products(id)
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total REAL NOT NULL,
                status TEXT DEFAULT 'pending',
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            );

            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor = await db.execute("SELECT COUNT(*) FROM categories")
        count = await cursor.fetchone()
        if count[0] == 0:
            await db.executescript("""
                INSERT INTO categories (name, emoji) VALUES
                    ('Burgers', '🍔'),
                    ('Pizza', '🍕'),
                    ('Drinks', '🥤'),
                    ('Desserts', '🍰');

                INSERT INTO products (category_id, name, description, price) VALUES
                    (1, 'Classic Burger', 'Beef patty, lettuce, tomato, cheese', 25000),
                    (1, 'Double Smash', 'Double beef patty with special sauce', 35000),
                    (1, 'Chicken Burger', 'Crispy fried chicken fillet', 28000),
                    (2, 'Margherita', 'Tomato sauce, mozzarella, basil', 40000),
                    (2, 'Pepperoni', 'Tomato sauce, mozzarella, pepperoni', 45000),
                    (3, 'Coca-Cola', 'Cold refreshing 500ml', 8000),
                    (3, 'Fresh Juice', 'Orange or apple, 400ml', 12000),
                    (4, 'Chocolate Cake', 'Rich chocolate slice', 15000),
                    (4, 'Ice Cream', 'Vanilla or chocolate scoop', 10000);
            """)
        await db.commit()

async def get_categories():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM categories")
        return await cursor.fetchall()

async def get_products_by_category(category_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM products WHERE category_id = ? AND available = 1", (category_id,)
        )
        return await cursor.fetchall()

async def get_product(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        return await cursor.fetchone()

async def get_all_products():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT p.*, c.name as category_name FROM products p JOIN categories c ON p.category_id = c.id"
        )
        return await cursor.fetchall()

async def add_product(category_id: int, name: str, description: str, price: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO products (category_id, name, description, price) VALUES (?, ?, ?, ?)",
            (category_id, name, description, price)
        )
        await db.commit()

async def toggle_product_availability(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE products SET available = CASE WHEN available = 1 THEN 0 ELSE 1 END WHERE id = ?",
            (product_id,)
        )
        await db.commit()

async def add_to_cart(user_id: int, product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ?",
            (user_id, product_id)
        )
        existing = await cursor.fetchone()
        if existing:
            await db.execute(
                "UPDATE cart SET quantity = quantity + 1 WHERE id = ?", (existing[0],)
            )
        else:
            await db.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, 1)",
                (user_id, product_id)
            )
        await db.commit()

async def get_cart(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT c.id, c.quantity, p.name, p.price, (c.quantity * p.price) as subtotal
            FROM cart c JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ?
        """, (user_id,))
        return await cursor.fetchall()

async def remove_from_cart(cart_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cart WHERE id = ?", (cart_id,))
        await db.commit()

async def clear_cart(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        await db.commit()

async def create_order(user_id: int, address: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cart_items = await get_cart(user_id)
        if not cart_items:
            return None

        total = sum(item["subtotal"] for item in cart_items)

        cursor = await db.execute(
            "INSERT INTO orders (user_id, total, address) VALUES (?, ?, ?)",
            (user_id, total, address)
        )
        order_id = cursor.lastrowid

        for item in cart_items:
            await db.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price) "
                "SELECT ?, product_id, quantity, p.price FROM cart c JOIN products p ON c.product_id = p.id WHERE c.id = ?",
                (order_id, item["id"])
            )

        await db.commit()
        await clear_cart(user_id)
        return order_id

async def get_user_orders(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
            (user_id,)
        )
        return await cursor.fetchall()

async def get_order_details(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT oi.*, p.name FROM order_items oi JOIN products p ON oi.product_id = p.id WHERE oi.order_id = ?",
            (order_id,)
        )
        return await cursor.fetchall()

async def get_all_orders():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM orders ORDER BY created_at DESC LIMIT 50"
        )
        return await cursor.fetchall()

async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        await db.commit()

async def add_review(user_id: int, order_id: int, rating: int, comment: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO reviews (user_id, order_id, rating, comment) VALUES (?, ?, ?, ?)",
            (user_id, order_id, rating, comment)
        )
        await db.commit()

async def get_reviews():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT r.*, o.address FROM reviews r JOIN orders o ON r.order_id = o.id ORDER BY r.created_at DESC LIMIT 20"
        )
        return await cursor.fetchall()

async def has_reviewed(user_id: int, order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM reviews WHERE user_id = ? AND order_id = ?", (user_id, order_id)
        )
        return await cursor.fetchone() is not None