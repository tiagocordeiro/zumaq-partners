# Generated by Django 2.1.5 on 2019-01-18 17:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0003_customproduto'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomCoeficiente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parceiro', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomCoeficienteItens',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coeficiente', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Coeficidente (%)')),
                ('parceiro', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('produto', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.Produto')),
            ],
        ),
        migrations.RemoveField(
            model_name='customproduto',
            name='parceiro',
        ),
        migrations.RemoveField(
            model_name='customproduto',
            name='produto',
        ),
        migrations.DeleteModel(
            name='CustomProduto',
        ),
    ]