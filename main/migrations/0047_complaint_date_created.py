# Generated by Django 3.2.9 on 2022-01-07 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0046_alter_userleavestatus_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='complaint',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
