# Generated by Django 3.1.2 on 2020-10-22 04:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_cotacoesmoedas'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='api_secret_key',
            field=models.CharField(blank=True, max_length=36, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='api_view',
            field=models.BooleanField(default=False, verbose_name='Habilitar API programática'),
        ),
    ]
