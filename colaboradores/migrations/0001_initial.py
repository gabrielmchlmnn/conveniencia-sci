# Generated by Django 4.2.1 on 2023-06-14 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Colaboradore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=70)),
                ('cpf', models.CharField(max_length=14, unique=True)),
                ('login', models.CharField(max_length=50, unique=True)),
                ('senha', models.CharField(max_length=30)),
            ],
        ),
    ]
