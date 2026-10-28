# wagtail_simple_forum/management/commands/forum_recalculate_stats.py
from django.core.management.base import BaseCommand
from wagtail_simple_forum.models import ForumTopic, PrivateMessageThread


class Command(BaseCommand):
    help = "Recalculates cached post counts, view counters, and last post metadata."

    def handle(self, *args, **options):
        self.stdout.write("Recalculating ForumTopic statistics...")
        topics = ForumTopic.objects.all()
        t_count = topics.count()
        for i, topic in enumerate(topics.iterator(), 1):
            topic.recalculate_stats()
            if i % 500 == 0 or i == t_count:
                self.stdout.write(f"  Processed {i}/{t_count} topics...")

        self.stdout.write("Recalculating PrivateMessageThread statistics...")
        threads = PrivateMessageThread.objects.all()
        th_count = threads.count()
        for i, thread in enumerate(threads.iterator(), 1):
            thread.recalculate_stats()
            if i % 500 == 0 or i == th_count:
                self.stdout.write(f"  Processed {i}/{th_count} threads...")

        self.stdout.write(self.style.SUCCESS("All forum statistics successfully recalculated!"))

