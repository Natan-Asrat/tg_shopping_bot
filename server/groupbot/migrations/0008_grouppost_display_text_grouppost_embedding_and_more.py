# Generated by Django 4.2.17 on 2025-05-14 21:07

from django.db import migrations, models
import pgvector.django.vector


class Migration(migrations.Migration):

    dependencies = [
        ("groupbot", "0007_enable_pgvector"),
    ]

    operations = [
        migrations.AddField(
            model_name="grouppost",
            name="display_text",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="grouppost",
            name="embedding",
            field=pgvector.django.vector.VectorField(
                blank=True,
                dimensions=512,
                help_text="Vector embeddings (clip-vit-large-patch14) of the file content",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="grouppost",
            name="tags",
            field=models.TextField(blank=True, null=True),
        ),
    ]
