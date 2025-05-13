from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from django.conf import settings
from my_tg_bot.handlers.start import start
from my_tg_bot.handlers.search import search, handle_search_mode_unavailable_post, handle_search_mode_available_post
from my_tg_bot.handlers.sellers import sellers
from my_tg_bot.handlers.buy_button import handle_buy_button
from my_tg_bot.handlers.confirm_intention import handle_buy_confirmation
from my_tg_bot.handlers.availability import handle_availability_response
from my_tg_bot.handlers.search import handle_older_post
from my_tg_bot.handlers.contact import handle_contact
from my_tg_bot.handlers.group_message import handle_group_message
from my_tg_bot.handlers.echo import echo

TOKEN = settings.TELEGRAM_TOKEN

def setup():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("sellers", sellers))

    application.add_handler(CallbackQueryHandler(handle_search_mode_unavailable_post, pattern=r'^search_mode_unavailable$'))
    application.add_handler(CallbackQueryHandler(handle_search_mode_available_post, pattern=r'^search_mode_available$'))
    application.add_handler(CallbackQueryHandler(handle_buy_button, pattern=r'^buy_'))
    application.add_handler(CallbackQueryHandler(handle_availability_response, pattern=r'^(confirm|deny)_avail_'))
    application.add_handler(CallbackQueryHandler(handle_buy_confirmation, pattern=r'^confirm_buy_'))
    application.add_handler(CallbackQueryHandler(handle_older_post, pattern=r'^older_post_'))

    application.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    application.add_handler(MessageHandler(filters.ChatType.GROUPS & (filters.TEXT | filters.PHOTO), handle_group_message))
    application.add_handler(MessageHandler(filters.TEXT, echo))
    print("Bot started with long polling...")
    application.run_polling()