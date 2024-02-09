# Generated by Django 4.2.7 on 2023-11-30 07:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("init", "0015_delete_log"),
    ]

    operations = [
        migrations.CreateModel(
            name="Log",
            fields=[
                ("index", models.AutoField(primary_key=True, serialize=False)),
                ("date_golajum", models.DateTimeField(auto_now_add=True)),
                ("date_checked", models.DateTimeField(null=True)),
                ("date_rated", models.DateTimeField(null=True)),
                ("rating", models.IntegerField(null=True)),
                ("sweet_rating", models.IntegerField(default=0)),
                ("sour_rating", models.IntegerField(default=0)),
                ("fizzy_rating", models.IntegerField(default=0)),
                ("body_rating", models.IntegerField(default=0)),
                ("strong_rating", models.IntegerField(default=0)),
                ("alc_range_rating", models.IntegerField(default=0)),
                (
                    "login_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="init.user"
                    ),
                ),
                (
                    "name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="init.output"
                    ),
                ),
            ],
        ),
    ]
