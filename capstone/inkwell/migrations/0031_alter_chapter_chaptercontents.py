# Generated by Django 4.2.1 on 2023-10-24 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inkwell', '0030_alter_chapter_chaptercontents'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chapter',
            name='chapterContents',
            field=models.TextField(),
        ),
    ]
