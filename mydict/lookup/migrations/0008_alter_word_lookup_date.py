# Generated by Django 5.0 on 2023-12-09 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lookup', '0007_alter_word_lookup_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='lookup_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Search date'),
        ),
    ]
