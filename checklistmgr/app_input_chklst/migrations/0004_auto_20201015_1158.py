# Generated by Django 3.1.1 on 2020-10-15 09:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_input_chklst', '0003_auto_20201015_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material',
            name='mat_material',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mat_secondary', to='app_input_chklst.material'),
        ),
    ]