# Generated by Django 4.2.1 on 2023-12-04 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inkwell', '0045_ink_coauthors'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ink',
            name='coAuthors',
        ),
    ]