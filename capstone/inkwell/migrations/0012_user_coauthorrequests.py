# Generated by Django 4.2.1 on 2023-09-19 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inkwell', '0011_user_followers'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='coAuthorRequests',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
