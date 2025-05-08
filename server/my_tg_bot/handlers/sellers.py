from telegram import Update
from telegram.ext import ContextTypes
from my_tg_bot.utils.buttons import get_restart_button

async def sellers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "sellers"
    await update.message.reply_text("What product sellers are you looking for?", reply_markup=get_restart_button())
