# Generated by Django 4.2.3 on 2023-09-12 07:39

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('inkwell', '0003_ink_privatestatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='ink',
            name='creation_date',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
    ]