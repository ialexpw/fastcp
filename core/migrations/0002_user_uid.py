# Generated by Django 3.2.6 on 2021-08-23 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='uid',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
