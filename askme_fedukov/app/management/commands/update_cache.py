from django.core.management.base import BaseCommand
from app.utils.cache import CacheManager
from app.models import Tag, Profile

class Command(BaseCommand):
    help = 'Updates all cached data'

    def handle(self, *args, **kwargs):
        tags = Tag.objects.get_hot_tags()
        best = Profile.objects.get_best_members()
        CacheManager(hot_tags=tags, best_members=best).push()
        self.stdout.write(self.style.SUCCESS('Cache updated successfully.'))