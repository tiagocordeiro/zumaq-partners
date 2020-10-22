# Generated by Django 3.1.2 on 2020-10-22 02:40

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20201021_2321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='api_secret_key',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
