# Generated by Django 4.2.1 on 2023-07-06 21:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0009_alter_produtos_cod_barras'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produtos',
            name='cod_barras',
            field=models.IntegerField(),
        ),
    ]