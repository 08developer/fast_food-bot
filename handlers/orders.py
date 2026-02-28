from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.db import get_user_orders, get_order_details
from keyboards.kb import order_status_kb

router = Router()

STATUS_EMOJI = {
    "pending": "🟡 Pending",
    "confirmed": "🔵 Confirmed",
    "preparing": "🟠 Preparing",
    "delivered": "🟢 Delivered",
    "cancelled": "🔴 Cancelled"
}


@router.message(F.text == "📦 My Orders")
async def my_orders(message: Message):
    orders = await get_user_orders(message.from_user.id)

    if not orders:
        await message.answer("📦 You haven't placed any orders yet.")
        return

    for order in orders[:5]:  # Show last 5 orders
        items = await get_order_details(order["id"])
        items_text = "\n".join(f"  • {i['name']} x{i['quantity']}" for i in items)
        status = STATUS_EMOJI.get(order["status"], order["status"])

        text = (
            f"📦 <b>Order #{order['id']}</b>\n"
            f"📅 {order['created_at'][:16]}\n"
            f"📍 {order['address']}\n\n"
            f"{items_text}\n\n"
            f"💰 Total: <b>{int(order['total']):,} so'm</b>\n"
            f"Status: <b>{status}</b>"
        )

        await message.answer(text, parse_mode="HTML", reply_markup=order_status_kb(order["id"]))


@router.callback_query(F.data.startswith("refresh_order:"))
async def refresh_order(callback: CallbackQuery):
    from database.db import get_user_orders
    order_id = int(callback.data.split(":")[1])
    orders = await get_user_orders(callback.from_user.id)
    order = next((o for o in orders if o["id"] == order_id), None)

    if not order:
        await callback.answer("Order not found.", show_alert=True)
        return

    status = STATUS_EMOJI.get(order["status"], order["status"])
    await callback.answer(f"Current status: {status}", show_alert=True)