from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from my_tg_bot.utils import replies

async def handle_buy_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    action, checking_msg_id = query.data.split('_')[1:]
    checking_msg_id = int(checking_msg_id)
    
    if action == "buy":
        # User confirmed to buy
        await query.edit_message_text(
            replies.on_responded_sure_buy(),
            parse_mode=ParseMode.HTML
        )