# wagtail_simple_forum/signals.py
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import ForumPost, ForumTopic, PrivateMessage


def _recalc_topic(topic_id):
    # Re-fetch by id: the instance's cached topic may be stale after bulk ops.
    topic = ForumTopic.objects.filter(pk=topic_id).first()
    if topic:
        topic.recalculate_stats()


@receiver(post_save, sender=ForumPost)
def update_topic_stats_on_save(sender, instance, created, update_fields, **kwargs):
    # Ordinary replies use atomic F() increments in views, so a recalculation
    # here would race with them. Updates only happen through moderation
    # (approve/hide) or post_edit — both rare — and neither path is guaranteed
    # to pass update_fields (the Wagtail admin form saves without it), so we
    # recalculate on every update to keep the denormalised counters correct.
    if not created and instance.topic_id:
        _recalc_topic(instance.topic_id)


@receiver(post_delete, sender=ForumPost)
def update_topic_stats_on_delete(sender, instance, **kwargs):
    if instance.topic_id:
        _recalc_topic(instance.topic_id)


@receiver(post_delete, sender=PrivateMessage)
def update_pm_thread_stats_on_delete(sender, instance, **kwargs):
    if instance.thread_id:
        try:
            instance.thread.recalculate_stats()
        except Exception:
            pass
