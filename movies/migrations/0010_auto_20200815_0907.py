# Generated by Django 3.0.6 on 2020-08-15 06:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('movies', '0009_remove_seance_sold_out'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seance',
            name='film',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='movies.Film'),
        ),
        migrations.AlterField(
            model_name='seance',
            name='hall',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='movies.Hall'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
