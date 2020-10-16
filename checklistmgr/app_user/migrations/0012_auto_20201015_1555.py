# Generated by Django 3.1.1 on 2020-10-15 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_user', '0011_auto_20201002_2313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='society', to='app_user.address', verbose_name='Address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_company',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='user_company', to='app_user.company'),
        ),
    ]