# Generated by Django 4.2.1 on 2023-11-14 10:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inkwell', '0041_coauthorrequest_acceptedstatus_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ink',
            name='letterCount',
        ),
    ]
