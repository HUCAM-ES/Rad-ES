# Generated by Django 2.1.2 on 2018-10-30 19:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dose_app', '0002_auto_20181030_1745'),
    ]

    operations = [
        migrations.AddField(
            model_name='modelstudyxa',
            name='study_time_parsed',
            field=models.TimeField(default=datetime.time(0, 0)),
        ),
    ]
