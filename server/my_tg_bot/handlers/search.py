from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from account.models import User
from asgiref.sync import sync_to_async
from my_tg_bot.utils.send_post import send_next_post
from my_tg_bot.utils.buttons import get_restart_button
import requests
from groupbot.models import SearchSession
from my_tg_bot.utils.search_results import get_sorted_posts_by_similarity
from telegram.constants import ParseMode
from django.conf import settings

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mode"] = "search"
    await update.message.reply_text("What kind of products are you looking for?", reply_markup=get_restart_button())

async def handle_search_mode_available_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    checking_msg_id = None
    for row in query.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data.startswith('confirm_buy_'):
                checking_msg_id = button.callback_data.split('_')[-1]
            elif button.callback_data.startswith('older_post_'):
                post_id = button.callback_data.split('_')[-1]
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes, I'm ready to buy", callback_data=f"confirm_buy_{checking_msg_id}")],
        [InlineKeyboardButton("👀 No, Show me another similar item", callback_data=f"older_post_{post_id}")]
    ])
    
    await query.edit_message_reply_markup(reply_markup=keyboard)
    
    context.user_data["mode"] = "search"
    await query.message.reply_text("What kind of products are you looking for?", reply_markup=get_restart_button())

async def handle_search_mode_unavailable_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    checking_msg_id = None
    for row in query.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data.startswith('confirm_buy_'):
                checking_msg_id = button.callback_data.split('_')[-1]
            elif button.callback_data.startswith('older_post_'):
                post_id = button.callback_data.split('_')[-1]
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Show similar items", callback_data=f"older_post_{post_id}"),
        ]
    ])
    
    await query.edit_message_reply_markup(reply_markup=keyboard)
    
    context.user_data["mode"] = "search"
    await query.message.reply_text("What kind of products are you looking for?", reply_markup=get_restart_button())

async def handle_older_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    

    current_post_id = int(query.data.split('_')[2])
    

    try:
        user = await sync_to_async(User.objects.get)(tg_id=query.from_user.id)
    except User.DoesNotExist:
        await query.edit_message_text("Please start the bot with /start first.")
        return
    

    try:
        await context.bot.edit_message_reply_markup(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Buy Now 🛍️", callback_data=f"buy_{current_post_id}")]
            ])
        )

    except Exception as e:
        print(f"Couldn't delete message: {e}")

    await send_next_post(user, context, current_post_id)

@sync_to_async
def get_embedding_from_text(text):
    response = requests.post(f"{settings.ENCODER_SERVER_SCHEME}://{settings.ENCODER_SERVER_HOST}:{settings.ENCODER_SERVER_PORT}/encode", json={"text": text}, timeout=10)
    response.raise_for_status()
    return response.json().get("embedding")

async def send_search_results_to_user(user, context: ContextTypes.DEFAULT_TYPE, query_text=None):
    # You need query text to generate embedding + tags
    if not query_text:
        await context.bot.send_message(chat_id=user.tg_id, text="Please send a search query first.")
        return

    # 1. Get user embedding and tags from query (you have a method for this)
    try:
        user_embedding = await get_embedding_from_text(query_text)  # your async function to get embedding vector
    except Exception as e:
        await context.bot.send_message(chat_id=user.tg_id, text="We are facing some issues. Please try again later.")
        print(f"Error getting embedding: {e}")
        return
    embedding = [float(x) for x in user_embedding] if isinstance(user_embedding, list) else user_embedding
    search_session = await sync_to_async(SearchSession.objects.create)(user=user, search_term=query_text, embedding=embedding)
    
    # 2. Get sorted post lists
    combined_results = await get_sorted_posts_by_similarity(search_session)
    if not combined_results:
        await context.bot.send_message(chat_id=user.tg_id, text="No posts available.")
        return
    
    for post in combined_results:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Buy Now 🛍️", callback_data=f"buy_{post.pk}"),
                *([InlineKeyboardButton("No! Show me another one...", callback_data=f"next_search_{search_session.pk}_{post.pk}_0")] if len(combined_results) == 1 else [])
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
    if len(combined_results) > 1:
        last_post = combined_results[-1]
        next_post_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Show me more!", callback_data=f"next_search_{search_session.pk}_{last_post.pk}_1")]
        ])

        await context.bot.send_message(
            chat_id=user.tg_id,
            text="Not what you're looking for?",
            reply_markup=next_post_keyboard
        )


async def handle_next_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    current_post_id = int(query.data.split('_')[3])
    separate_message = int(query.data.split('_')[4])

    search_session_id = int(query.data.split('_')[2])
    

    try:
        search_session = await sync_to_async(SearchSession.objects.get)(pk=search_session_id)
    except SearchSession.DoesNotExist:
        await query.edit_message_text("Please start the bot with /start first.")
        return
    # 2. Get sorted post lists
    combined_results = await get_sorted_posts_by_similarity(search_session)
    if not combined_results:
        await context.bot.send_message(chat_id=query.message.chat.id, text="No posts available.")
        return
    
    for post in combined_results:
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Buy Now 🛍️", callback_data=f"buy_{post.pk}"),
                *([InlineKeyboardButton("No! Show me another one...", callback_data=f"next_search_{search_session.pk}_{post.pk}_0")] if len(combined_results) == 1 else [])
            ]
        ])
        if post.image_links:
            media_group = []
            for i, img_link in enumerate(post.image_links):
                caption = post.text if i == 0 else None
                media_group.append(InputMediaPhoto(media=img_link, caption=caption))
            
            await context.bot.send_media_group(
                chat_id=query.message.chat.id,
                media=media_group
            )

            await context.bot.send_message(
                chat_id=query.message.chat.id,
                text="Are you interested in buying this item?",
                reply_markup=keyboard
            )
        else:
            await context.bot.send_message(
                chat_id=query.message.chat.id,
                text=post.text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    if len(combined_results) > 1:
        last_post = combined_results[-1]
        next_post_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Show me more!", callback_data=f"next_search_{search_session.pk}_{last_post.pk}_1")]
        ])

        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="Not what you're looking for?",
            reply_markup=next_post_keyboard
        )


    try:
        if separate_message == 1:
            await context.bot.delete_message(
                chat_id=query.message.chat.id,
                message_id=query.message.message_id
            )
        else:
            await context.bot.edit_message_reply_markup(
                chat_id=query.message.chat.id,
                message_id=query.message.message_id,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Buy Now 🛍️", callback_data=f"buy_{current_post_id}")]
                ])
            )

    except Exception as e:
        print(f"Couldn't delete message: {e}")
