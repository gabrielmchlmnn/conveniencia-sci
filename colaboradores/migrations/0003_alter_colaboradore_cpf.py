# Generated by Django 4.2.1 on 2023-06-22 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colaboradores', '0002_colaboradore_situacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='colaboradore',
            name='cpf',
            field=models.CharField(max_length=14),
        ),
    ]
