# Generated by Django 2.0.7 on 2018-08-02 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("challenges", "0006_externalchallenge")]

    operations = [
        migrations.RemoveField(model_name="challenge", name="header_image"),
        migrations.RemoveField(model_name="challenge", name="logo_path"),
    ]
