# Generated by Django 4.2.7 on 2023-12-04 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brand', '0002_alter_brand_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='brand',
            name='soft_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
