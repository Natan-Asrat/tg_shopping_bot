from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from django.conf import settings
from my_tg_bot.handlers.start import start
from my_tg_bot.handlers.search import search, handle_search_mode_unavailable_post, handle_search_mode_available_post
from my_tg_bot.handlers.sellers import sellers
from my_tg_bot.handlers.buy_button import handle_buy_button
from my_tg_bot.handlers.confirm_intention import handle_buy_confirmation
from my_tg_bot.handlers.availability import handle_availability_response
from my_tg_bot.handlers.search import handle_older_post, handle_next_search
from my_tg_bot.handlers.contact import handle_contact
from my_tg_bot.handlers.group_message import handle_group_message
from my_tg_bot.handlers.echo import echo
from my_tg_bot.handlers.register_bot import register_bot, handle_token, cancel
from groupbot.models import UserBot
from telegram.ext import  ContextTypes


class MyContext(ContextTypes.DEFAULT_TYPE):
    def __init__(self, is_default: bool, user_bot: UserBot):
        self.is_default = is_default
        self.user_bot = user_bot

def create_bot_application(token, is_default=True, user_bot=None):
    application = Application.builder().token(token).build()
    application.bot_data['my_context'] = MyContext(is_default, user_bot)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("sellers", sellers))

    application.add_handler(CallbackQueryHandler(handle_search_mode_unavailable_post, pattern=r'^search_mode_unavailable$'))
    application.add_handler(CallbackQueryHandler(handle_search_mode_available_post, pattern=r'^search_mode_available$'))
    application.add_handler(CallbackQueryHandler(handle_buy_button, pattern=r'^buy_'))
    application.add_handler(CallbackQueryHandler(handle_availability_response, pattern=r'^(confirm|deny)_avail_'))
    application.add_handler(CallbackQueryHandler(handle_buy_confirmation, pattern=r'^confirm_buy_'))
    application.add_handler(CallbackQueryHandler(handle_older_post, pattern=r'^older_post_'))
    application.add_handler(CallbackQueryHandler(handle_next_search, pattern=r'^next_search_'))

    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.ChatType.GROUPS & (filters.TEXT | filters.PHOTO), handle_group_message))
    application.add_handler(CommandHandler("registerbot", register_bot))
    # Bot registration conversation handler
    register_conversation = ConversationHandler(
        entry_points=[CommandHandler("registerbot", register_bot)],
        states={
            1: [MessageHandler(filters.TEXT, handle_token)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(register_conversation)

    application.add_handler(MessageHandler(filters.TEXT, echo))
    return application
import threading
import asyncio
import time
from telegram.ext import Application

def start_bot_thread(token, is_default=True, user_bot=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_bot(token, is_default=is_default, user_bot=user_bot))

async def start_bot(token, is_default=True, user_bot=None):
    application = create_bot_application(token, is_default=is_default, user_bot=user_bot)
    print(f"Bot started with polling: {token}")

    # Safer than run_polling() in threads
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Keep the bot running (forever)
    await asyncio.Event().wait()
import psutil
import os
bot_threads = {}
def monitor_bot_threads(interval=60):
    process = psutil.Process(os.getpid())

    print("[MONITOR] Tracking only started bot threads", flush=True)
    while True:
        total_rss = process.memory_info().rss
        print(f"\n[MEMORY] Total RSS: {total_rss / 1024 / 1024:.2f} MB", flush=True)

        threads = {t.id: t for t in process.threads()}
        total_cpu = 0.0
        bot_cpu_times = {}

        for name, thread in bot_threads.items():
            native_id = thread.native_id or thread.ident
            ps_thread = threads.get(native_id)

            if ps_thread:
                cpu_time = ps_thread.user_time + ps_thread.system_time
                bot_cpu_times[name] = cpu_time
                total_cpu += cpu_time

        for name, cpu_time in bot_cpu_times.items():
            proportion = cpu_time / total_cpu if total_cpu > 0 else 0
            estimated_rss = total_rss * proportion
            print(f"  Bot '{name}' → CPU: {cpu_time:.2f}s | Est. RSS: {estimated_rss / 1024 / 1024:.2f} MB", flush=True)

        for name in bot_threads:
            if name not in bot_cpu_times:
                print(f"  Bot '{name}' → Not found in psutil", flush=True)

        time.sleep(interval)

def setup():
    active_bots = UserBot.objects.filter(is_active=True)
    print(f"Found {active_bots.count()} active bots")

    for bot in active_bots:
        print(f"Starting bot: {bot.token}", flush=True)
        bot_dict = {
            'token': bot.token, 
            'username': bot.username,
            'name': bot.name,
            'description': bot.description,
            'is_active': bot.is_active,
            'created_at': bot.created_at,
            'updated_at': bot.updated_at
        } 
        thread = threading.Thread(target=start_bot_thread, args=(bot.token, False, bot_dict), daemon=True)
        thread.start()
        bot_threads[bot.token] = thread

    thread = threading.Thread(target=start_bot_thread, args=(settings.TELEGRAM_TOKEN, True, None), daemon=True)
    thread.start()
    bot_threads["default"] = thread

    monitor_thread = threading.Thread(target=monitor_bot_threads, daemon=True)
    monitor_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down bots.")