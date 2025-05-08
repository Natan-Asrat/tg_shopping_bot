from telegram import Update
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from groupbot.models import GroupPost

async def handle_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    

    if message.chat.type not in ['group', 'supergroup']:
        return

    text = message.text or message.caption or ""
    

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
    else:
        post = await sync_to_async(GroupPost.objects.create)(
            group_id=message.chat.id,
            message_id=message.message_id,
            text=text,
            image_links=image_links
        )
