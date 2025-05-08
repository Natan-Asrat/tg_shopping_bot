from telegram import Update
from telegram.ext import ContextTypes
from account.models import User
from asgiref.sync import sync_to_async
from my_tg_bot.utils.buttons import get_main_buttons

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact

    if contact and contact.user_id == update.effective_user.id:
        try:
            user = await sync_to_async(User.objects.get)(tg_id=contact.user_id)
            user.phone = contact.phone_number
            await sync_to_async(user.save)()
            await update.message.reply_text("Phone number saved. Thank you!")
            await update.message.reply_text("Do you want to find products or sellers?", reply_markup=get_main_buttons())
        except User.DoesNotExist:
            await update.message.reply_text("User not found.")
    else:
        await update.message.reply_text("Please share your *own* contact.", parse_mode="Markdown")
