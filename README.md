# 🍔 FastFood Telegram Bot

A Telegram bot I built for a fast food business using Python and aiogram 3. 
Users can browse the menu, add items to their cart, place orders and track them — all without leaving Telegram.

---

## What it can do

**For customers:**
- Browse the menu by category
- Add items to cart and remove them
- Place an order with a delivery address
- Check order status
- Rate and review their order after delivery

**For admins:**
- See all incoming orders and update their status
- Add new products to the menu or disable existing ones
- Read customer reviews
- Access everything via /admin command

---

## Built with

- Python 3.11
- aiogram 3 — async Telegram bot framework
- SQLite + aiosqlite — lightweight database
- FSM (Finite State Machine) — for multi-step conversations
- python-dotenv — for keeping secrets out of the code

---

## How to run it

1. Clone the repo and go into the folder
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Create a `.env` file:
```
BOT_TOKEN=your_token_here
ADMIN_IDS=your_telegram_id
```
4. Run:
```bash
python main.py
```

---

## Project structure
```
├── main.py
├── config.py
├── database/
│   └── db.py
├── handlers/
│   ├── user.py
│   ├── cart.py
│   ├── orders.py
│   ├── reviews.py
│   └── admin.py
└── keyboards/
    └── kb.py
```

---

## What I learned

This project taught me a lot about structuring a real Python project properly. 
Working with async code was new to me at first but aiogram 3 made it click. 
I also got comfortable with SQLite, designing tables with relationships, and 
thinking about how real users would actually interact with a bot.