from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from account.models import User
from asgiref.sync import sync_to_async
from my_tg_bot.handlers.buy_button import handle_buy_button
from my_tg_bot.handlers.start import start
from my_tg_bot.handlers.search import search
from my_tg_bot.handlers.sellers import sellers
from my_tg_bot.utils.send_post import send_latest_post_to_user
from my_tg_bot.utils.buttons import get_main_buttons, get_restart_button
from my_tg_bot.handlers.register_bot import register_bot, handle_token

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.message.from_user
    text = update.message.text.strip().lower()
    if update.callback_query:
        query = update.callback_query
        if query.data.startswith("buy_"):
            return await handle_buy_button(update, context)
        else:
            return

    if update.message.chat.type != 'private':

        if text == "help":
            return await update.message.reply_text("Use /start in private chat to access all features.")
        return

    try:
        user = await sync_to_async(User.objects.get)(tg_id=tg_user.id)
    except User.DoesNotExist:
        return await start(update, context)

    if not user.phone:
        button = [[KeyboardButton("Share Phone", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(button, one_time_keyboard=True, resize_keyboard=True)
        return await update.message.reply_text("Please share your phone number.", reply_markup=reply_markup)

    if text == "search products":
        return await search(update, context)
    elif text == "view sellers":
        return await sellers(update, context)
    elif text == "help":
        return await update.message.reply_text("Use /search or /sellers to switch modes.\nUse /start to reset.")
    elif text == "start again":
        return await start(update, context)
    elif text == "register your bot":
        return await register_bot(update, context)

    mode = context.user_data.get("mode")
    if mode == "sellers":
        return await update.message.reply_text("This is seller mode.", reply_markup=get_restart_button())
    elif mode == "search":
        await send_latest_post_to_user(user, context)
        return
    elif mode == "register_bot":
        return await handle_token(update, context)
    else:
        return await update.message.reply_text("Do you want to find products or sellers?", reply_markup=get_main_buttons())
