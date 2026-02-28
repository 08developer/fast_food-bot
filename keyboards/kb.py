from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def main_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🍽️ Menu"),
        KeyboardButton(text="🛒 My Cart")
    )
    builder.row(
        KeyboardButton(text="📦 My Orders"),
        KeyboardButton(text="⭐ Leave Review")
    )
    return builder.as_markup(resize_keyboard=True)


def categories_kb(categories) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(
            text=f"{cat['emoji']} {cat['name']}",
            callback_data=f"category:{cat['id']}"
        )
    builder.adjust(2)
    return builder.as_markup()


def products_kb(products, category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in products:
        builder.button(
            text=f"{p['name']} — {int(p['price']):,} so'm",
            callback_data=f"product:{p['id']}"
        )
    builder.button(text="⬅️ Back to Categories", callback_data="back_to_categories")
    builder.adjust(1)
    return builder.as_markup()


def product_detail_kb(product_id: int, category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Add to Cart", callback_data=f"add_to_cart:{product_id}")
    builder.button(text="⬅️ Back", callback_data=f"category:{category_id}")
    builder.adjust(1)
    return builder.as_markup()


def cart_kb(cart_items) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in cart_items:
        builder.button(
            text=f"❌ Remove {item['name']}",
            callback_data=f"remove_cart:{item['id']}"
        )
    builder.button(text="✅ Place Order", callback_data="place_order")
    builder.button(text="🗑️ Clear Cart", callback_data="clear_cart")
    builder.adjust(1)
    return builder.as_markup()


def order_status_kb(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Refresh Status", callback_data=f"refresh_order:{order_id}")
    builder.button(text="⭐ Review this order", callback_data=f"review_order:{order_id}")
    builder.adjust(1)
    return builder.as_markup()


def rating_kb(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i in range(1, 6):
        stars = "⭐" * i
        builder.button(text=stars, callback_data=f"rate:{order_id}:{i}")
    builder.adjust(5)
    return builder.as_markup()


def skip_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Skip comment", callback_data="skip_comment")
    return builder.as_markup()


def admin_menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📋 All Orders"),
        KeyboardButton(text="🍔 Manage Menu")
    )
    builder.row(
        KeyboardButton(text="⭐ View Reviews"),
        KeyboardButton(text="👤 User Mode")
    )
    return builder.as_markup(resize_keyboard=True)


def admin_orders_kb(orders) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    status_emoji = {
        "pending": "🟡",
        "confirmed": "🔵",
        "preparing": "🟠",
        "delivered": "🟢",
        "cancelled": "🔴"
    }
    for order in orders:
        emoji = status_emoji.get(order["status"], "⚪")
        builder.button(
            text=f"{emoji} Order #{order['id']} — {int(order['total']):,} so'm",
            callback_data=f"admin_order:{order['id']}"
        )
    builder.adjust(1)
    return builder.as_markup()


def admin_order_actions_kb(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    statuses = [
        ("🔵 Confirm", "confirmed"),
        ("🟠 Preparing", "preparing"),
        ("🟢 Delivered", "delivered"),
        ("🔴 Cancel", "cancelled"),
    ]
    for label, status in statuses:
        builder.button(text=label, callback_data=f"set_status:{order_id}:{status}")
    builder.button(text="⬅️ Back", callback_data="back_to_orders")
    builder.adjust(2)
    return builder.as_markup()


def admin_products_kb(products) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for p in products:
        status = "✅" if p["available"] else "❌"
        builder.button(
            text=f"{status} {p['name']} ({p['category_name']})",
            callback_data=f"toggle_product:{p['id']}"
        )
    builder.button(text="➕ Add New Product", callback_data="add_product")
    builder.adjust(1)
    return builder.as_markup()


def admin_categories_kb(categories) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.button(
            text=f"{cat['emoji']} {cat['name']}",
            callback_data=f"admin_select_category:{cat['id']}"
        )
    builder.adjust(2)
    return builder.as_markup()