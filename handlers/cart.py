from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import add_to_cart, get_cart, remove_from_cart, clear_cart, create_order
from keyboards.kb import cart_kb, main_menu_kb

router = Router()


class OrderState(StatesGroup):
    waiting_for_address = State()


@router.callback_query(F.data.startswith("add_to_cart:"))
async def add_item_to_cart(callback: CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    await add_to_cart(callback.from_user.id, product_id)
    await callback.answer("✅ Added to cart!", show_alert=False)


@router.message(F.text == "🛒 My Cart")
async def show_cart(message: Message):
    cart = await get_cart(message.from_user.id)

    if not cart:
        await message.answer("🛒 Your cart is empty!\n\nBrowse our 🍽️ Menu to add items.")
        return

    text = "🛒 <b>Your Cart:</b>\n\n"
    total = 0
    for item in cart:
        text += f"• {item['name']} x{item['quantity']} — {int(item['subtotal']):,} so'm\n"
        total += item["subtotal"]
    text += f"\n💰 <b>Total: {int(total):,} so'm</b>"

    await message.answer(text, parse_mode="HTML", reply_markup=cart_kb(cart))


@router.callback_query(F.data.startswith("remove_cart:"))
async def remove_cart_item(callback: CallbackQuery):
    cart_id = int(callback.data.split(":")[1])
    await remove_from_cart(cart_id)

    cart = await get_cart(callback.from_user.id)
    if not cart:
        await callback.message.edit_text("🛒 Your cart is now empty.")
        return

    text = "🛒 <b>Your Cart:</b>\n\n"
    total = 0
    for item in cart:
        text += f"• {item['name']} x{item['quantity']} — {int(item['subtotal']):,} so'm\n"
        total += item["subtotal"]
    text += f"\n💰 <b>Total: {int(total):,} so'm</b>"

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=cart_kb(cart))
    await callback.answer("Removed!")


@router.callback_query(F.data == "clear_cart")
async def handle_clear_cart(callback: CallbackQuery):
    await clear_cart(callback.from_user.id)
    await callback.message.edit_text("🗑️ Cart cleared.")
    await callback.answer()


@router.callback_query(F.data == "place_order")
async def place_order_start(callback: CallbackQuery, state: FSMContext):
    cart = await get_cart(callback.from_user.id)
    if not cart:
        await callback.answer("Your cart is empty!", show_alert=True)
        return

    await state.set_state(OrderState.waiting_for_address)
    await callback.message.answer(
        "📍 Please send your delivery address:\n\n"
        "Example: <i>Tashkent, Chilanzar district, Buyuk Ipak Yuli 78, apt 12</i>",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(OrderState.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    address = message.text.strip()
    order_id = await create_order(message.from_user.id, address)

    if not order_id:
        await message.answer("❌ Something went wrong. Please try again.")
        await state.clear()
        return

    await state.clear()
    await message.answer(
        f"✅ <b>Order #{order_id} placed successfully!</b>\n\n"
        f"📍 Delivery to: {address}\n"
        f"⏳ Status: <b>Pending</b>\n\n"
        f"We'll confirm your order shortly. Thank you! 🙏",
        parse_mode="HTML",
        reply_markup=main_menu_kb()
    )