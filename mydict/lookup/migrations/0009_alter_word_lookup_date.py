# Generated by Django 5.0 on 2023-12-10 13:38

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lookup', '0008_alter_word_lookup_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='lookup_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
