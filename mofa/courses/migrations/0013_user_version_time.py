# Generated by Django 2.2.6 on 2020-01-27 13:45

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0012_auto_20200127_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='version_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
