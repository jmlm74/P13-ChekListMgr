# Generated by Django 3.1.1 on 2020-09-30 20:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0006_auto_20200928_1423'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'ordering': ['company_name'], 'verbose_name': 'Company', 'verbose_name_plural': 'Companies'},
        ),
        migrations.RenameField(
            model_name='company',
            old_name='name',
            new_name='company_name',
        ),
    ]
