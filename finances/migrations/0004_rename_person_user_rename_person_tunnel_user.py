# Generated by Django 4.2.6 on 2023-10-12 19:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0003_rename_personstock_tunnel'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Person',
            new_name='User',
        ),
        migrations.RenameField(
            model_name='tunnel',
            old_name='person',
            new_name='user',
        ),
    ]
