# Generated by Django 2.2 on 2019-04-08 21:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_produto_imagem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='imagem',
            field=models.URLField(blank=True, default='https://via.placeholder.com/150', null=True),
        ),
    ]
