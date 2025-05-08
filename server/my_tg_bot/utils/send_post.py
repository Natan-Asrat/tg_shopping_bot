from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from asgiref.sync import sync_to_async
from telegram.ext import ContextTypes
from groupbot.models import GroupPost
from telegram.constants import ParseMode

async def send_next_post(user, context: ContextTypes.DEFAULT_TYPE, last_post_id=None):
    """Send the next older post after last_post_id"""
    try:

        if last_post_id:
            post = await sync_to_async(
                lambda: GroupPost.objects.filter(
                    id__lt=last_post_id
                ).order_by('-created_at').first()
            )()
        else:

            post = await sync_to_async(
                lambda: GroupPost.objects.order_by('-created_at').first()
            )()

        if not post:
            await context.bot.send_message(
                chat_id=user.tg_id,
                text="No more similar posts available." if last_post_id else "No posts available."
            )
            return

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Buy Now 🛍️", callback_data=f"buy_{post.pk}"),
                InlineKeyboardButton("No! Show me another one...", callback_data=f"older_post_{post.pk}")
            ]
        ])

        if post.image_links:
            media_group = []
            for i, img_link in enumerate(post.image_links):
                caption = post.text if i == 0 else None
                media_group.append(InputMediaPhoto(media=img_link, caption=caption))
            
            await context.bot.send_media_group(
                chat_id=user.tg_id,
                media=media_group
            )
            await context.bot.send_message(
                chat_id=user.tg_id,
                text="Are you interested in this item?",
                reply_markup=keyboard
            )
        else:
            await context.bot.send_message(
                chat_id=user.tg_id,
                text=post.text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        print(f"Failed to send post to user {user.tg_id}: {str(e)}")

async def send_latest_post_to_user(user, context: ContextTypes.DEFAULT_TYPE):
    try:

        post = await sync_to_async(
            lambda: GroupPost.objects.order_by('-created_at').first()
        )()

        if not post:
            await context.bot.send_message(chat_id=user.tg_id, text="No posts available.")
            return

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Buy Now 🛍️", callback_data=f"buy_{post.pk}"),
                InlineKeyboardButton("No! Show me another one...", callback_data=f"older_post_{post.pk}")
            ]
        ])
        if post.image_links:
            media_group = []
            for i, img_link in enumerate(post.image_links):
                caption = post.text if i == 0 else None
                media_group.append(InputMediaPhoto(media=img_link, caption=caption))
            
            await context.bot.send_media_group(
                chat_id=user.tg_id,
                media=media_group
            )

            await context.bot.send_message(
                chat_id=user.tg_id,
                text="Are you interested in buying this item?",
                reply_markup=keyboard
            )
        else:
            await context.bot.send_message(
                chat_id=user.tg_id,
                text=post.text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        print(f"Failed to send latest post to user {user.tg_id}: {str(e)}")
