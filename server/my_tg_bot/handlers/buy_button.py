from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from account.models import User
from asgiref.sync import sync_to_async
from groupbot.models import GroupPost
from my_tg_bot.utils import replies

async def handle_buy_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    post_id = int(query.data.split('_')[1])

    post = await sync_to_async(GroupPost.objects.get)(id=post_id)

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Please wait...", callback_data="checking_availability")
    ]])

    checking_msg = await query.edit_message_text(
        replies.on_buy_button_clicked_checking_availability(post.text),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    user = update.effective_user

    try:
        support_user = await sync_to_async(User.objects.get)(username="emi_shop_support")

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"confirm_avail_{post_id}_{user.id}_{checking_msg.message_id}"),
                InlineKeyboardButton("❌ No", callback_data=f"deny_avail_{post_id}_{user.id}_{checking_msg.message_id}")
            ]
        ])
        if post.image_links:
            media_group = []
            for i, img_link in enumerate(post.image_links):
                caption = replies.on_availability_check_request(post.text) if i == 0 else None
                media_group.append(InputMediaPhoto(media=img_link, caption=caption))
            
            await context.bot.send_media_group(
                chat_id=support_user.tg_id,
                media=media_group
            )

            await context.bot.send_message(
                chat_id=support_user.tg_id,
                text="Please confirm availability:",
                reply_markup=keyboard
            )
        else:
            await context.bot.send_message(
                chat_id=support_user.tg_id,
                text=replies.on_availability_check_request(post.text),
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        await context.bot.send_message(
            chat_id=user.id,
            text=replies.on_notified_seller_response()
        )
        
    except Exception:
        await context.bot.send_message(
            chat_id=user.id,
            text=replies.on_couldnt_reach_seller()
        )
        await query.edit_message_text(
            text=replies.on_couldnt_reach_seller_edit_post(),
            parse_mode=ParseMode.HTML
        )
