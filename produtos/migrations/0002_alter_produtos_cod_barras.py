# Generated by Django 4.2.1 on 2023-06-14 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produtos',
            name='cod_barras',
            field=models.IntegerField(unique=True),
        ),
    ]