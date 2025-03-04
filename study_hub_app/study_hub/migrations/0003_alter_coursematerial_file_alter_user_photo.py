# Generated by Django 5.1.5 on 2025-02-14 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("study_hub", "0002_alter_coursematerial_file_alter_user_photo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="coursematerial",
            name="file",
            field=models.FileField(upload_to="course_materials/"),
        ),
        migrations.AlterField(
            model_name="user",
            name="photo",
            field=models.ImageField(blank=True, null=True, upload_to="profile_photos/"),
        ),
    ]
