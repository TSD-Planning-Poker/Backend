# Generated by Django 4.0.4 on 2022-05-03 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_room_closed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userstory',
            name='description',
            field=models.CharField(max_length=500),
        ),
    ]