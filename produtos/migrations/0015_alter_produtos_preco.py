# Generated by Django 4.2.1 on 2023-07-27 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0014_alter_produtos_situacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produtos',
            name='preco',
            field=models.DecimalField(decimal_places=2, max_digits=200),
        ),
    ]
