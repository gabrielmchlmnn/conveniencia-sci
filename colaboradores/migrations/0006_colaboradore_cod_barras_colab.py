# Generated by Django 4.2.1 on 2023-07-28 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colaboradores', '0005_alter_colaboradore_situacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='colaboradore',
            name='cod_barras_colab',
            field=models.CharField(default='1009463', max_length=10),
        ),
    ]