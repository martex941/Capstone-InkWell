# Generated by Django 4.2.1 on 2023-10-24 09:01

from django.db import migrations
import django_quill.fields


class Migration(migrations.Migration):

    dependencies = [
        ('inkwell', '0027_delete_inkversioncontrol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='chapterContents',
            field=django_quill.fields.QuillField(),
        ),
    ]