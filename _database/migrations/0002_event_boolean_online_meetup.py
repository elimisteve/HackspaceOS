# Generated by Django 3.0.4 on 2020-03-28 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('_database', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='boolean_online_meetup',
            field=models.BooleanField(default=False),
        ),
    ]
