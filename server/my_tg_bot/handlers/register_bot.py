from telegram import Update
from telegram.ext import ContextTypes
import aiohttp
from account.models import User
from groupbot.models import UserBot
from asgiref.sync import sync_to_async
from my_tg_bot.utils.buttons import get_registration_buttons, get_main_buttons
import threading 

async def register_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates the bot registration process."""
    await update.message.reply_text(
        "Let's register your AI bot! 🤖\n"
        "Please send me your bot token from @BotFather.\n\n"
        "To get a token:\n"
        "1. Go to @BotFather\n"
        "2. Create a new bot with /newbot\n"
        "3. Copy the token and send it here\n\n"
        "Type /cancel to cancel the process.",
        reply_markup=get_registration_buttons()
    )
    context.user_data["mode"] = "register_bot"


async def handle_token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the bot token input and attempts to register the bot."""
    if context.user_data.get("mode") != "register_bot":
        return

    if update.message.text.lower() == "cancel":
        return await cancel(update, context)

    token = update.message.text
    await update.message.delete()

    try:
        # Validate the token via Telegram API
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.telegram.org/bot{token}/getMe") as resp:
                data = await resp.json()

        if not data.get("ok"):
            await update.message.reply_text(
                "❌ Invalid bot token. Please double-check it and try again.",
                reply_markup=get_registration_buttons()
            )
            return

        bot_info = data["result"]
        bot_name = bot_info["first_name"]
        bot_username = bot_info["username"]

        # Check if already registered
        is_existing = await sync_to_async(UserBot.objects.filter(token=token).exists)()
        if is_existing:
            await update.message.reply_text(
                "❌ This bot is already registered.\n"
                "Please use another token or /cancel the process.",
                reply_markup=get_registration_buttons()
            )
            return

        # Get the current user and save bot
        user = await sync_to_async(User.objects.get)(tg_id=update.effective_user.id)
        new_bot = await sync_to_async(UserBot.objects.create)(
            owner=user,
            name=bot_name,
            username=bot_username,
            token=token
        )
        
        from my_tg_bot.utils.setup import start_bot_thread
        from my_tg_bot.utils.setup import bot_threads
        def launch_new_bot():
            thread = threading.Thread(
                target=start_bot_thread,
                args=(new_bot.token, False, {
                    'token': new_bot.token,
                    'username': new_bot.username,
                    'name': new_bot.name,
                    'description': new_bot.description,
                    'is_active': new_bot.is_active,
                    'created_at': new_bot.created_at,
                    'updated_at': new_bot.updated_at
                }),
                daemon=True
            )
            thread.start()
            bot_threads[new_bot.token] = thread

        await sync_to_async(launch_new_bot)()

        context.user_data.pop("mode", None)

        await update.message.reply_text(
            f"✅ Bot successfully registered!\n\n"
            f"Bot Name: {bot_name}\n"
            f"Username: @{bot_username}\n\n"
            f"Now you can add it to your groups and start using AI features.",
            reply_markup=get_main_buttons()
        )

    except Exception as e:
        await update.message.reply_text(
            "❌ An error occurred while verifying your bot.\n"
            "Please try again later or use /cancel to stop the process.",
            reply_markup=get_registration_buttons()
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels the registration process."""
    context.user_data.pop("mode", None)
    await update.message.reply_text(
        "Registration cancelled. Use /registerbot to try again.",
        reply_markup=get_main_buttons()
    )
