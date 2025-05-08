from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from account.models import User
from asgiref.sync import sync_to_async
from groupbot.models import GroupPost

async def handle_buy_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    post_id = int(query.data.split('_')[1])

    post = await sync_to_async(GroupPost.objects.get)(id=post_id)

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("Please wait...", callback_data="checking_availability")
    ]])

    await query.edit_message_text(
        f"{post.text}\n\n{'='*30}\n\n🔍 Checking availability... Please wait",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    user = update.effective_user

    try:
        support_user = await sync_to_async(User.objects.get)(username="emi_shop_support")

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data=f"confirm_avail_{post_id}_{user.id}"),
                InlineKeyboardButton("❌ No", callback_data=f"deny_avail_{post_id}_{user.id}")
            ]
        ])
        if post.image_links:
            media_group = []
            for i, img_link in enumerate(post.image_links):
                caption = f"🛒 Availability Check Request\n\nFrom: @{user.username}\n\nIs this item still available?\n\n{post.text}" if i == 0 else None
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
                text=f"🛒 Availability Check Request\n\nFrom: @{user.username}\n\nIs this item still available?\n\n{post.text}",
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        await context.bot.send_message(
            chat_id=user.id,
            text="📬 We've notified the seller about your request. They'll respond shortly!"
        )
        
    except Exception:
        await context.bot.send_message(
            chat_id=user.id,
            text="⚠️ Couldn't reach seller. Please try again later."
        )
        await query.edit_message_text(
            text=f"{post.text}\n\n{'='*30}\n\n⚠️ Couldn't process your request. Please try again.",
            parse_mode=ParseMode.HTML
        )
