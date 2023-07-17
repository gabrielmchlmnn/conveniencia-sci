# Generated by Django 4.2.1 on 2023-07-13 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0012_delete_estoque'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produtos',
            name='tipo',
            field=models.CharField(choices=[('Alimento', 'Alimento'), ('Ingresso', 'Ingresso'), ('Roupa', 'Roupa')], max_length=8),
        ),
    ]