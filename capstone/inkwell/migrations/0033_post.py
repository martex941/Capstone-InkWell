# Generated by Django 4.2.1 on 2023-10-27 08:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inkwell', '0032_alter_chapter_chaptercontents'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('referencedPostInk', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='referencedPostInk', to='inkwell.ink')),
            ],
        ),
    ]