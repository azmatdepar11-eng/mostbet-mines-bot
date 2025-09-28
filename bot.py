import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN missing!")

GRID_SIZE = 5
user_ids = {}  # memory dict {telegram_id: mostbet_id}

def recommend_strategy(amount: float):
    if amount < 50:
        mines = 3
    elif amount < 200:
        mines = 4
    elif amount < 500:
        mines = 6
    else:
        mines = 8

    corners = [(1,1),(1,GRID_SIZE),(GRID_SIZE,1),(GRID_SIZE,GRID_SIZE)]
    idx = int(amount) % 4
    first = corners[idx]
    clicks = [first]

    r,c = first
    if c+1 <= GRID_SIZE:
        clicks.append((r, c+1))
    else:
        clicks.append((r+1 if r+1<=GRID_SIZE else r, c-1))

    r2,c2 = clicks[-1]
    third = (min(GRID_SIZE, r2+1), min(GRID_SIZE, c2+1))
    clicks.append(third)

    grid = [["🔵" for _ in range(GRID_SIZE)] for __ in range(GRID_SIZE)]
    for (rr,cc) in clicks:
        grid[rr-1][cc-1] = "⭐"
    ascii_grid = "\n".join("".join(row) for row in grid)
    return mines, clicks, ascii_grid

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_ids:
        await update.message.reply_text(
            "👋 Bhai! Pehle apni Mostbet ID bhej do (sirf ek dafa).\n"
            "Example: `ID1234567`"
        )
    else:
        await update.message.reply_text(
            f"👋 Welcome back! Tumhari Mostbet ID: {user_ids[user_id]}\n"
            "Ab sirf bet amount bhejo (e.g. `100`)."
        )

async def save_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in user_ids and text.upper().startswith("ID"):
        user_ids[user_id] = text
        await update.message.reply_text(
            f"✅ Mostbet ID save ho gayi: {text}\nAb bet amount bhejo (e.g. 100)."
        )
    elif user_id not in user_ids:
        await update.message.reply_text("❌ Pehle valid Mostbet ID bhejo (e.g. ID123456).")
    else:
        # user already registered → treat message as bet amount
        try:
            amount = float(text)
        except:
            await update.message.reply_text("❌ Sirf number bhejo (e.g. 100).")
            return
        mines, clicks, ascii_grid = recommend_strategy(amount)
        clicks_str = ", ".join([f"({r},{c})" for r,c in clicks])
        reply = (
            f"Bet: {int(amount)} PKR\n"
            f"Suggested mines: {mines}\n"
            f"Clicks: {clicks_str}\n\n"
            f"{ascii_grid}"
        )
        await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), save_id))
    app.run_polling()

if __name__ == "__main__":
    main()
