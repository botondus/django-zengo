# Generated by Django 2.1.4 on 2019-01-22 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("zengo", "0002_auto_20190122_0600")]

    operations = [
        migrations.AddField(
            model_name="zendeskuser",
            name="photos_json",
            field=models.TextField(blank=True, null=True),
        )
    ]
