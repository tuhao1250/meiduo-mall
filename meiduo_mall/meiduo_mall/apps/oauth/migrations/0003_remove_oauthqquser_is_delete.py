# Generated by Django 2.1.8 on 2019-06-11 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0002_remove_oauthqquser_is_delete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='oauthqquser',
            name='is_delete',
        ),
    ]
