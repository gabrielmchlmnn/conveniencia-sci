# Generated by Django 4.2.1 on 2023-07-05 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produtos', '0006_produtos_tipo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produtos',
            name='tipo',
            field=models.CharField(choices=[('ALimento', 'Alimento'), ('Ingresso', 'Ingresso')], max_length=20),
        ),
    ]
