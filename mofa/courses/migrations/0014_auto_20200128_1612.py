# Generated by Django 2.2.6 on 2020-01-28 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0013_user_version_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='version_time',
            field=models.DateTimeField(null=True),
        ),
    ]
