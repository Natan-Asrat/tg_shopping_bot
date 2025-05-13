from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from asgiref.sync import sync_to_async
from groupbot.models import GroupPost
from my_tg_bot.utils import replies

async def handle_availability_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Parse the callback data
    status, _, post_id, user_id, checking_msg_id = query.data.split('_')
    post_id = int(post_id)
    user_id = int(user_id)
    checking_msg_id = int(checking_msg_id)
    
    post = await sync_to_async(GroupPost.objects.get)(id=post_id)
    
    if status == "confirm":
        # Update the original message
        await query.edit_message_text(
            replies.on_confirm_availability_edit_text_for_seller(post.text),
            parse_mode=ParseMode.HTML
        )
        
        # Send message to the customer with confirmation buttons
        confirmation_msg = await context.bot.send_message(
            chat_id=user_id,
            text=replies.on_confirmed_availability_response(),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Yes, I'm ready to buy", callback_data=f"confirm_buy_{checking_msg_id}")],
                [InlineKeyboardButton("👀 No, Show me another similar item", callback_data=f"older_post_{post_id}")],
                [InlineKeyboardButton("🔍 Search other things", callback_data="search_mode_available")]
            ]),
            parse_mode=ParseMode.HTML
        )
        
        # Update the checking availability message
        await context.bot.edit_message_text(
            chat_id=user_id,
            message_id=checking_msg_id,
            text=replies.on_confirm_availability_edit_text_for_buyer(post.text),
            parse_mode=ParseMode.HTML
        )
    
    elif status == "deny":
        
        # Update the original message
        await query.edit_message_text(
            replies.on_deny_availability_edit_text_for_seller(post.text),
            parse_mode=ParseMode.HTML
        )
        
        # Send message to customer with alternative options
        await context.bot.send_message(
            chat_id=user_id,
            text=replies.on_deny_availability_response(),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("Show similar items", callback_data=f"older_post_{post_id}"),
                    InlineKeyboardButton("🔍 Back to search", callback_data="search_mode_unavailable")
                ]
            ]),
            parse_mode=ParseMode.HTML
        )
        
        # Update the checking availability message
        await context.bot.edit_message_text(
            chat_id=user_id,
            message_id=checking_msg_id,
            text=replies.on_deny_availability_edit_text_for_buyer(post.text),
            parse_mode=ParseMode.HTML
        )
