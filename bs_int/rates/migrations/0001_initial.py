# Generated by Django 5.0.3 on 2024-04-02 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DataSet",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("one_month", models.FloatField()),
                ("two_month", models.FloatField()),
                ("three_month", models.FloatField()),
                ("four_month", models.FloatField()),
                ("six_month", models.FloatField()),
                ("one_year", models.FloatField()),
                ("two_year", models.FloatField()),
                ("three_year", models.FloatField()),
                ("five_year", models.FloatField()),
                ("seven_year", models.FloatField()),
                ("ten_year", models.FloatField()),
                ("twenty_year", models.FloatField()),
                ("thirty_year", models.FloatField()),
            ],
        ),
        migrations.AddConstraint(
            model_name="dataset",
            constraint=models.UniqueConstraint(models.F("date"), name="unique_date"),
        ),
    ]