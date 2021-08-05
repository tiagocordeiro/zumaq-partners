# Generated by Django 3.2.5 on 2021-07-29 17:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pedidos', '0009_auto_20210420_1036'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='separado',
            field=models.BooleanField(default=False, verbose_name='Pedido separado'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='separado_data',
            field=models.DateTimeField(blank=True, null=True, verbose_name='separado em'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='separado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gerente', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='pedidoitem',
            name='separado',
            field=models.BooleanField(default=False, verbose_name='Item separado'),
        ),
        migrations.AddField(
            model_name='pedidoitem',
            name='separado_imagem',
            field=models.ImageField(blank=True, null=True, upload_to='pedidos-separacao/'),
        ),
        migrations.AddField(
            model_name='pedidoitem',
            name='separado_nota',
            field=models.TextField(blank=True, null=True, verbose_name='Observações'),
        ),
    ]