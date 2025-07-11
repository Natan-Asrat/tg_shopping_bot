# Generated by Django 4.2.17 on 2025-05-05 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GroupPost",
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
                ("group_id", models.BigIntegerField()),
                ("message_id", models.BigIntegerField()),
                ("text", models.TextField(blank=True, null=True)),
                ("image_links", models.JSONField(default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "unique_together": {("group_id", "message_id")},
            },
        ),
    ]
