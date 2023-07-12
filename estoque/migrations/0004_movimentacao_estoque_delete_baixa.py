# Generated by Django 4.2.1 on 2023-07-11 13:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('estoque', '0003_alter_baixa_data'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movimentacao_estoque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(default=django.utils.timezone.now)),
                ('quantidade', models.IntegerField()),
                ('tipo', models.BooleanField()),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('produto', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='estoque.estoque')),
            ],
        ),
        migrations.DeleteModel(
            name='Baixa',
        ),
    ]
