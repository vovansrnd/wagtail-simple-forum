"""
Copy forum data from a legacy Django app (e.g. the old project-local ``forum``
app) into wagtail-simple-forum tables.

Both apps share the same field layout, so the copy is a row-by-row remap with
primary-key translation for Category -> Section -> Topic -> Post and PM
Thread -> PM. Rows are matched by ``legacy_id`` / old pk, which makes the
command idempotent: re-running it only copies what is missing.

Usage:
    python manage.py forum_import_from_app --source forum [--recalc] [--dry-run]

Run it while BOTH apps are installed (INSTALLED_APPS contains the old app and
``wagtail_simple_forum``). Afterwards switch the URLs to the plugin, then drop
the old app.
"""

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from wagtail_simple_forum.models import (
    ForumCategory,
    ForumLegacyUserMap,
    ForumPost,
    ForumSection,
    ForumTopic,
    PrivateMessage,
    PrivateMessageThread,
)

# (source model name, target model, FK field -> role of the pk map)
PLAN = [
    ("ForumCategory", ForumCategory, {}),
    ("ForumSection", ForumSection, {"category": "ForumCategory"}),
    ("ForumTopic", ForumTopic, {"section": "ForumSection"}),
    ("ForumPost", ForumPost, {"topic": "ForumTopic"}),
    ("PrivateMessageThread", PrivateMessageThread, {}),
    ("PrivateMessage", PrivateMessage, {"thread": "PrivateMessageThread"}),
    ("ForumLegacyUserMap", ForumLegacyUserMap, {}),
]

BATCH_SIZE = 500


def _shared_fields(source_model, target_model):
    source_fields = {f.attname for f in source_model._meta.concrete_fields}
    skip = {"id", "pk"}
    return [f.attname for f in target_model._meta.concrete_fields
            if f.attname in source_fields and f.attname not in skip]


class Command(BaseCommand):
    help = "Import forum data from a legacy app into wagtail_simple_forum (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--source", default="forum",
                            help="App label of the old forum app (default: forum)")
        parser.add_argument("--recalc", action="store_true",
                            help="Recalculate topic/thread statistics after import")
        parser.add_argument("--dry-run", action="store_true",
                            help="Only report what would be copied")

    @transaction.atomic
    def handle(self, *args, **options):
        source_app = options["source"]
        try:
            apps.get_app_config(source_app)
        except LookupError:
            raise CommandError(f"App '{source_app}' is not installed.")

        # old pk -> new pk, per source model name
        pk_maps = {}

        for source_name, target_model, fk_roles in PLAN:
            source_model = apps.get_model(source_app, source_name)

            fields = _shared_fields(source_model, target_model)
            # legacy models keep their old pk in `legacy_id`
            legacy_ids = set(
                target_model.objects.exclude(legacy_id__isnull=True)
                .values_list("legacy_id", flat=True)
            )
            pk_map = dict(
                target_model.objects.exclude(legacy_id__isnull=True)
                .values_list("legacy_id", "pk")
            )

            batch, copied, skipped = [], 0, 0
            source_qs = source_model.objects.order_by("pk").iterator(chunk_size=BATCH_SIZE)

            for row in source_qs:
                old_pk = row.pk
                if old_pk in legacy_ids:
                    skipped += 1
                    continue

                data = {}
                for attname in fields:
                    if attname == "legacy_id":
                        data["legacy_id"] = old_pk
                        continue
                    if attname.endswith("_id"):
                        base = attname[:-3]
                        if base in fk_roles:
                            old_fk = getattr(row, attname)
                            submap = pk_maps[fk_roles[base]]
                            data[attname] = submap.get(old_fk)
                            continue
                    data[attname] = getattr(row, attname)

                obj = target_model(**data)
                batch.append(obj)

                if len(batch) >= BATCH_SIZE:
                    created = target_model.objects.bulk_create(batch, batch_size=BATCH_SIZE)
                    for old_id, new_obj in zip(
                        [b.legacy_id for b in batch], created
                    ):
                        pk_map[old_id] = new_obj.pk
                    copied += len(batch)
                    batch = []

            if batch:
                created = target_model.objects.bulk_create(batch, batch_size=BATCH_SIZE)
                for old_id, new_obj in zip([b.legacy_id for b in batch], created):
                    pk_map[old_id] = new_obj.pk
                copied += len(batch)

            pk_maps[source_name] = pk_map
            self.stdout.write(
                f"{source_name}: copied {copied}, already present {skipped}"
            )

        if options["dry_run"]:
            # Откат в самом конце: set_rollback внутри цикла ломает
            # последующие модели (TransactionManagementError).
            self.stdout.write(self.style.WARNING("Dry run: nothing was saved."))
            transaction.set_rollback(True)
            return

        if options["recalc"]:
            for topic in ForumTopic.objects.all().only("pk").iterator():
                topic.recalculate_stats()
            self.stdout.write("Topic statistics recalculated.")

        self.stdout.write(self.style.SUCCESS("Done."))
