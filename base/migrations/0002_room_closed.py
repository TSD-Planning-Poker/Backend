# Generated by Django 4.0.4 on 2022-05-03 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='closed',
            field=models.BooleanField(default=False),
        ),
    ]