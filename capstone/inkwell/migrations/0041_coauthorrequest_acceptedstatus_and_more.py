# Generated by Django 4.2.1 on 2023-11-14 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inkwell', '0040_rename_requestedcontentchange_coauthorrequest_chaptercontents'),
    ]

    operations = [
        migrations.AddField(
            model_name='coauthorrequest',
            name='acceptedStatus',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coauthorrequest',
            name='declinedMessage',
            field=models.TextField(default=''),
        ),
    ]