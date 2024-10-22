# Generated by Django 4.2.1 on 2023-09-06 15:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inkwell', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Well',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wellOwner', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='well_owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=64)),
                ('content', models.TextField()),
                ('inkOwner', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='ink_owner', to=settings.AUTH_USER_MODEL)),
                ('wellOrigin', models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='well_pk', to='inkwell.well')),
            ],
        ),
    ]
