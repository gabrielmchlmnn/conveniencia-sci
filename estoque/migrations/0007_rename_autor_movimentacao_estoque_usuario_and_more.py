# Generated by Django 4.2.1 on 2023-07-11 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0006_alter_movimentacao_estoque_tipo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movimentacao_estoque',
            old_name='autor',
            new_name='usuario',
        ),
        migrations.AlterField(
            model_name='movimentacao_estoque',
            name='tipo',
            field=models.CharField(choices=[('Saída', 'Saída'), ('Entrada', 'Entrada')], max_length=7),
        ),
    ]
