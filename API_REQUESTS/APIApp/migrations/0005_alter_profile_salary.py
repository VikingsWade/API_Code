# Generated by Django 5.0.2 on 2024-02-27 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('APIApp', '0004_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='salary',
            field=models.IntegerField(default=0),
        ),
    ]