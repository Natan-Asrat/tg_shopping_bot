from django.core.management.base import BaseCommand
from my_tg_bot.utils.setup import setup

class Command(BaseCommand):
    help = "Run Telegram bot with long polling"

    def handle(self, *args, **kwargs):
        setup()
        