from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import  ContextTypes
from account.models import User
from asgiref.sync import sync_to_async
from my_tg_bot.utils.buttons import get_main_buttons

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.message.from_user

    if update.message.chat.type != 'private':
        return await update.message.reply_text("Please start the bot in private chat to access all features.")

    try:
        user = await sync_to_async(User.objects.get)(tg_id=tg_user.id)
    except User.DoesNotExist:
        user = await sync_to_async(User.objects.create)(
            tg_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name
        )

    if not user.phone:
        button = [[KeyboardButton("Share Phone", request_contact=True)]]
        reply_markup = ReplyKeyboardMarkup(button, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "Hello! Please share your phone number.\nThere is a button below your keyboard.",
            reply_markup=reply_markup
        )
    else:
        welcome_msg = "Welcome back! "
        if 'current_group_id' in context.user_data:
            welcome_msg += "I'm showing you products from a specific group. "
            welcome_msg += "Use /cleargroup to see products from all groups. "
        welcome_msg += "What would you like to do today?"
        
        await update.message.reply_text(
            welcome_msg,
            reply_markup=get_main_buttons()
        )
