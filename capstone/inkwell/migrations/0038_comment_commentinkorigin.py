# Generated by Django 4.2.1 on 2023-11-03 09:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inkwell', '0037_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='commentInkOrigin',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='commentInkOrigin', to='inkwell.ink'),
        ),
    ]
