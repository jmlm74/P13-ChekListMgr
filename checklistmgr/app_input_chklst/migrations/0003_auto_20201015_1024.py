# Generated by Django 3.1.1 on 2020-10-15 08:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_input_chklst', '0002_auto_20201014_1603'),
    ]

    operations = [
        migrations.RenameField(
            model_name='material',
            old_name='mat_Type',
            new_name='mat_type',
        ),
    ]
