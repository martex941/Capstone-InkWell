# Generated by Django 4.2.1 on 2023-10-29 15:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inkwell', '0034_post_postcreationdate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='followers',
        ),
    ]
