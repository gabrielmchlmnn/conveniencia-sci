# Generated by Django 4.2.1 on 2023-07-05 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('colaboradores', '0003_alter_colaboradore_cpf'),
    ]

    operations = [
        migrations.AddField(
            model_name='colaboradore',
            name='email',
            field=models.EmailField(default='michelmanngabriel@gmail.com', max_length=254),
        ),
    ]
