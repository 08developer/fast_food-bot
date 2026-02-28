from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.db import get_user_orders, add_review, has_reviewed
from keyboards.kb import rating_kb, skip_kb

router = Router()


class ReviewState(StatesGroup):
    waiting_for_comment = State()


@router.message(F.text == "⭐ Leave Review")
async def leave_review(message: Message):
    orders = await get_user_orders(message.from_user.id)
    delivered = [o for o in orders if o["status"] == "delivered"]

    if not delivered:
        await message.answer(
            "⭐ You can only review delivered orders.\n\n"
            "Place an order first and wait for delivery! 🚀"
        )
        return

    order = delivered[0]
    already_reviewed = await has_reviewed(message.from_user.id, order["id"])
    if already_reviewed:
        await message.answer("✅ You've already reviewed your latest order. Thank you!")
        return

    await message.answer(
        f"⭐ <b>Rate your Order #{order['id']}</b>\n\nHow was your experience?",
        parse_mode="HTML",
        reply_markup=rating_kb(order["id"])
    )


@router.callback_query(F.data.startswith("review_order:"))
async def review_from_order(callback: CallbackQuery):
    order_id = int(callback.data.split(":")[1])
    already = await has_reviewed(callback.from_user.id, order_id)
    if already:
        await callback.answer("You already reviewed this order!", show_alert=True)
        return

    await callback.message.answer(
        f"⭐ <b>Rate Order #{order_id}</b>\n\nHow was your experience?",
        parse_mode="HTML",
        reply_markup=rating_kb(order_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("rate:"))
async def process_rating(callback: CallbackQuery, state: FSMContext):
    _, order_id, rating = callback.data.split(":")
    await state.update_data(order_id=int(order_id), rating=int(rating))
    await state.set_state(ReviewState.waiting_for_comment)

    stars = "⭐" * int(rating)
    await callback.message.answer(
        f"You rated: {stars}\n\n"
        f"💬 Would you like to leave a comment? (or skip)",
        reply_markup=skip_kb()
    )
    await callback.answer()


@router.message(ReviewState.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    await add_review(message.from_user.id, data["order_id"], data["rating"], message.text)
    await state.clear()
    await message.answer(
        "✅ Thank you for your review! We'll keep improving. 🙏",
    )


@router.callback_query(F.data == "skip_comment", ReviewState.waiting_for_comment)
async def skip_comment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await add_review(callback.from_user.id, data["order_id"], data["rating"], "")
    await state.clear()
    await callback.message.answer("✅ Thank you for your rating! 🙏")
    await callback.answer()