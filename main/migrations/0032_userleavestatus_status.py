# Generated by Django 3.2.9 on 2022-01-05 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0031_auto_20220104_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='userleavestatus',
            name='status',
            field=models.CharField(default='Pending', max_length=100),
        ),
    ]
