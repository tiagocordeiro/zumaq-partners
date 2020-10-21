# Generated by Django 3.1.2 on 2020-10-21 18:45

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_cotacoesmoedas'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='api_secret_key',
            field=models.CharField(default=core.models.make_secret, max_length=36, unique=True, verbose_name='Secret key needed for no logged json viewing'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='api_view',
            field=models.BooleanField(default=False, verbose_name='Habilitar API programática'),
        ),
    ]
