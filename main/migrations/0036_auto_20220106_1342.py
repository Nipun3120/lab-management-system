# Generated by Django 3.2.9 on 2022-01-06 13:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_complaint_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='userleavestatus',
            name='rejected',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='complaint',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='main.staff'),
        ),
    ]
