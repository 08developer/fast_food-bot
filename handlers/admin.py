from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_IDS
from database.db import (
    get_all_orders, get_order_details, update_order_status,
    get_all_products, toggle_product_availability,
    get_categories, add_product, get_reviews
)
from keyboards.kb import (
    admin_menu_kb, admin_orders_kb, admin_order_actions_kb,
    admin_products_kb, admin_categories_kb, main_menu_kb
)

router = Router()


class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in ADMIN_IDS


class AddProductState(StatesGroup):
    category = State()
    name = State()
    description = State()
    price = State()


# ─── Admin entry ──────────────────────────────────────────────────────────────

@router.message(IsAdmin(), F.text == "/admin")
async def admin_panel(message: Message):
    await message.answer(
        "👑 <b>Admin Panel</b>\n\nWelcome back, boss!",
        parse_mode="HTML",
        reply_markup=admin_menu_kb()
    )


@router.message(IsAdmin(), F.text == "👤 User Mode")
async def user_mode(message: Message):
    await message.answer("Switched to user mode.", reply_markup=main_menu_kb())


# ─── Orders management ────────────────────────────────────────────────────────

@router.message(IsAdmin(), F.text == "📋 All Orders")
async def all_orders(message: Message):
    orders = await get_all_orders()
    if not orders:
        await message.answer("No orders yet.")
        return
    await message.answer(
        f"📋 <b>All Orders</b> ({len(orders)} total):",
        parse_mode="HTML",
        reply_markup=admin_orders_kb(orders)
    )


@router.callback_query(F.data.startswith("admin_order:"))
async def admin_order_detail(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    items = await get_order_details(order_id)

    items_text = "\n".join(f"  • {i['name']} x{i['quantity']} — {int(i['price'] * i['quantity']):,} so'm" for i in items)

    await callback.message.edit_text(
        f"📦 <b>Order #{order_id}</b>\n\n{items_text}\n\nChoose new status:",
        parse_mode="HTML",
        reply_markup=admin_order_actions_kb(order_id)
    )


@router.callback_query(F.data.startswith("set_status:"))
async def set_order_status(callback: CallbackQuery):
    _, order_id, status = callback.data.split(":")
    await update_order_status(int(order_id), status)
    await callback.answer(f"✅ Order #{order_id} → {status}", show_alert=True)

    orders = await get_all_orders()
    await callback.message.edit_text(
        f"📋 <b>All Orders</b> ({len(orders)} total):",
        parse_mode="HTML",
        reply_markup=admin_orders_kb(orders)
    )


@router.callback_query(F.data == "back_to_orders")
async def back_to_orders(callback: CallbackQuery):
    orders = await get_all_orders()
    await callback.message.edit_text(
        f"📋 <b>All Orders</b> ({len(orders)} total):",
        parse_mode="HTML",
        reply_markup=admin_orders_kb(orders)
    )


# ─── Menu management ──────────────────────────────────────────────────────────

@router.message(IsAdmin(), F.text == "🍔 Manage Menu")
async def manage_menu(message: Message):
    products = await get_all_products()
    await message.answer(
        "🍔 <b>Manage Menu</b>\n\nTap a product to toggle availability, or add a new one:",
        parse_mode="HTML",
        reply_markup=admin_products_kb(products)
    )


@router.callback_query(F.data.startswith("toggle_product:"))
async def toggle_product(callback: CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    await toggle_product_availability(product_id)
    products = await get_all_products()
    await callback.message.edit_text(
        "🍔 <b>Manage Menu</b>",
        parse_mode="HTML",
        reply_markup=admin_products_kb(products)
    )
    await callback.answer("Toggled!")


@router.callback_query(F.data == "add_product")
async def add_product_start(callback: CallbackQuery, state: FSMContext):
    categories = await get_categories()
    await state.set_state(AddProductState.category)
    await callback.message.answer(
        "➕ <b>Add New Product</b>\n\nSelect a category:",
        parse_mode="HTML",
        reply_markup=admin_categories_kb(categories)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_select_category:"), AddProductState.category)
async def add_product_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split(":")[1])
    await state.update_data(category_id=category_id)
    await state.set_state(AddProductState.name)
    await callback.message.answer("📝 Enter product name:")
    await callback.answer()


@router.message(AddProductState.name)
async def add_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProductState.description)
    await message.answer("📝 Enter product description:")


@router.message(AddProductState.description)
async def add_product_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProductState.price)
    await message.answer("💰 Enter price (in so'm, numbers only):")


@router.message(AddProductState.price)
async def add_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.replace(",", "").replace(" ", ""))
    except ValueError:
        await message.answer("❌ Invalid price. Please enter a number:")
        return

    data = await state.get_data()
    await add_product(data["category_id"], data["name"], data["description"], price)
    await state.clear()
    await message.answer(
        f"✅ Product <b>{data['name']}</b> added for {int(price):,} so'm!",
        parse_mode="HTML"
    )


# ─── Reviews ──────────────────────────────────────────────────────────────────

@router.message(IsAdmin(), F.text == "⭐ View Reviews")
async def view_reviews(message: Message):
    reviews = await get_reviews()
    if not reviews:
        await message.answer("No reviews yet.")
        return

    text = "⭐ <b>Recent Reviews:</b>\n\n"
    for r in reviews:
        stars = "⭐" * r["rating"]
        comment = r["comment"] or "No comment"
        text += f"{stars} — Order #{r['order_id']}\n💬 {comment}\n\n"

    await message.answer(text, parse_mode="HTML")