# Generated by Django 5.1.5 on 2025-02-15 21:26

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("study_hub", "0003_alter_coursematerial_file_alter_user_photo"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedback",
            name="rating",
            field=models.IntegerField(
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(5),
                ],
            ),
        ),
    ]
