# Generated by Django 2.1.5 on 2019-02-11 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_customcoeficiente_coeficiente_padrao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customcoeficiente',
            name='coeficiente_padrao',
            field=models.DecimalField(decimal_places=2, default=0.5, max_digits=10, verbose_name='Coeficidente padrão (%)'),
        ),
    ]