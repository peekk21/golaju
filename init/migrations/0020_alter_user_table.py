# Generated by Django 4.2.7 on 2023-12-13 21:34

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("init", "0019_golajum_alter_user_options"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="user",
            table="init_user",
        ),
    ]
