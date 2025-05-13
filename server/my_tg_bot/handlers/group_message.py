from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommandScopeChat, ChatPermissions
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from groupbot.models import GroupPost
from django.conf import settings

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    my_context = context.application.bot_data.get('my_context')
    bot_username = my_context.user_bot.get('username') if not my_context.is_default else settings.BOT_USERNAME
    print('bot_username', bot_username)

    if message.chat.type not in ['group', 'supergroup']:
        return
        
    # Check if bot is admin and can send messages
    chat_member = await context.bot.get_chat_member(message.chat.id, context.bot.id)
    if chat_member.status not in ['administrator', 'member']:
        return

    text = message.text or message.caption or " "
    

    image_links = []
    if message.photo:

        file_id = message.photo[-1].file_id
        image_links.append(file_id)
    

    if message.media_group_id:
        existing_post = await sync_to_async(
            lambda: GroupPost.objects.filter(media_group_id=message.media_group_id).first()
        )()

        if existing_post:

            existing_post.image_links += image_links
            await sync_to_async(existing_post.save)()
        else:

            post = await sync_to_async(GroupPost.objects.create)(
                group_id=message.chat.id,
                message_id=message.message_id,
                text=text,
                image_links=image_links,
                media_group_id=message.media_group_id
            )
            
            # Add Ask AI button
            # Create deep link with group_id
            start_param = f"group_{message.chat.id}"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🤖 Ask AI", url=f"https://t.me/{bot_username}?start={start_param}")]
            ])
            await message.reply_text(
                "Search more products with AI!",
                reply_markup=keyboard,
                reply_to_message_id=message.message_id
            )
    else:
        post = await sync_to_async(GroupPost.objects.create)(
            group_id=message.chat.id,
            message_id=message.message_id,
            text=text,
            image_links=image_links
        )
        
        # Add Ask AI button
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Ask AI", url=f"https://t.me/{bot_username}")]
        ])
        await message.reply_text(
            "Search more products with AI!",
            reply_markup=keyboard,
            reply_to_message_id=message.message_id
        )
