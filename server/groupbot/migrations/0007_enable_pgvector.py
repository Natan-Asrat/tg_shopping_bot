# Generated by Django 5.1.2 on 2024-10-27 18:18
from pgvector.django import VectorExtension

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("groupbot", "0006_delete_groupsettings"),
    ]

    operations = [
        VectorExtension(),
    ]
