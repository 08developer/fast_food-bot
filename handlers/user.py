from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from database.db import get_categories, get_products_by_category, get_product
from keyboards.kb import main_menu_kb, categories_kb, products_kb, product_detail_kb

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"👋 Welcome to <b>FastFood Bot</b>, {message.from_user.first_name}!\n\n"
        "We deliver hot & fresh food right to your door. 🚀\n\n"
        "Use the menu below to get started:",
        parse_mode="HTML",
        reply_markup=main_menu_kb()
    )


@router.message(F.text == "🍽️ Menu")
async def show_menu(message: Message):
    categories = await get_categories()
    await message.answer(
        "📂 Choose a category:",
        reply_markup=categories_kb(categories)
    )


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery):
    categories = await get_categories()
    await callback.message.edit_text(
        "📂 Choose a category:",
        reply_markup=categories_kb(categories)
    )


@router.callback_query(F.data.startswith("category:"))
async def show_products(callback: CallbackQuery):
    category_id = int(callback.data.split(":")[1])
    products = await get_products_by_category(category_id)

    if not products:
        await callback.answer("No products in this category yet.", show_alert=True)
        return

    await callback.message.edit_text(
        "🍽️ Choose a product:",
        reply_markup=products_kb(products, category_id)
    )


@router.callback_query(F.data.startswith("product:"))
async def show_product_detail(callback: CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    product = await get_product(product_id)

    if not product:
        await callback.answer("Product not found.", show_alert=True)
        return

    text = (
        f"<b>{product['name']}</b>\n\n"
        f"📝 {product['description']}\n\n"
        f"💰 Price: <b>{int(product['price']):,} so'm</b>"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=product_detail_kb(product_id, product["category_id"])
    )