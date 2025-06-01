from django.core.management.base import BaseCommand
from app.utils.notification import CentrifugoMain

class Command(BaseCommand):
    help = 'Updates all cached data'

    def add_arguments(self, parser):
        parser.add_argument(
            'message',
            type=str,
            help='The message to publish via CentrifugoIndex'
        )

    def handle(self, *args, **kwargs):
        message = kwargs['message']
        CentrifugoMain().publish(message)
        self.stdout.write(self.style.SUCCESS('Successfully published message: %s' % message))