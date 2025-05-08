from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from account.models import User
from asgiref.sync import sync_to_async
from my_tg_bot.utils.send_post import send_next_post
from my_tg_bot.utils.buttons import get_restart_button

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "search"
    await update.message.reply_text("What kind of products are you looking for?", reply_markup=get_restart_button())



async def handle_older_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    

    current_post_id = int(query.data.split('_')[2])
    

    try:
        user = await sync_to_async(User.objects.get)(tg_id=query.from_user.id)
    except User.DoesNotExist:
        await query.edit_message_text("Please start the bot with /start first.")
        return
    

    try:
        await context.bot.edit_message_reply_markup(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Buy Now 🛍️", callback_data=f"buy_{current_post_id}")]
            ])
        )

    except Exception as e:
        print(f"Couldn't delete message: {e}")

    await send_next_post(user, context, current_post_id)

