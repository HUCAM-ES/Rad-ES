# Generated by Django 2.1.2 on 2018-10-30 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dose_app', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modelstudyxa',
            name='study_time_parsed',
        ),
        migrations.AlterField(
            model_name='modelstudyxa',
            name='study_time',
            field=models.CharField(default='000000.000000', max_length=32),
        ),
    ]
