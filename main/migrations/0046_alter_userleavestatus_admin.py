# Generated by Django 3.2.9 on 2022-01-07 11:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_alter_userleavestatus_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userleavestatus',
            name='admin',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='admin', to='main.staff'),
        ),
    ]
