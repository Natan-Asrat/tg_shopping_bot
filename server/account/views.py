from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Initialize your Telegram bot with your token
TOKEN = "YOUR_BOT_TOKEN"

# Define command handler for /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Hello! Please share your phone number.')

# Define message handler for text messages
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    if text.lower() == "hi":
        await update.message.reply_text('Hi there! Please send your phone number.')
    else:
        await update.message.reply_text(f'You said: {text}')

# Set up webhook to handle incoming updates from Telegram
@csrf_exempt
def webhook(request):
    json_str = request.body.decode("UTF-8")
    update = Update.de_json(json_str, bot)  # Deserialize incoming update
    
    # Create an Application instance with the bot
    application = Application.builder().token(TOKEN).build()

    # Add handlers for the commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the dispatcher to handle the incoming update
    application.update_queue.put(update)

    return JsonResponse({"status": "ok"})

# Set webhook to Telegram
@csrf_exempt
def set_webhook(request):
    """
    Sets the webhook with Telegram to point to your Django server's URL
    """
    # The webhook URL should be publicly accessible
    webhook_url = 'https://your_domain.com/webhook/'  # Replace this URL with your deployed domain or ngrok URL during development
    response = bot.setWebhook(webhook_url)
    return JsonResponse({"status": "Webhook set", "response": response})

