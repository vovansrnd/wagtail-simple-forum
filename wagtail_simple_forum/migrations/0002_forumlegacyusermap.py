import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wagtail_simple_forum", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ForumLegacyUserMap",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("legacy_id", models.PositiveIntegerField(unique=True)),
                ("legacy_username", models.CharField(blank=True, max_length=200)),
                ("display_name", models.CharField(blank=True, max_length=255)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("admin", "Admin"),
                            ("moderator", "Moderator"),
                            ("user", "User"),
                        ],
                        default="user",
                        max_length=20,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="forum_legacy_map",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Legacy user map",
                "verbose_name_plural": "Legacy user maps",
                "ordering": ["legacy_id"],
            },
        ),
    ]
