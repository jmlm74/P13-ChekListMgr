# Generated by Django 3.1.1 on 2020-10-15 18:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0012_auto_20201015_1555'),
        ('app_input_chklst', '0005_auto_20201015_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='mat_company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mat_company', to='app_user.company'),
        ),
    ]
