# Generated by Django 4.2.7 on 2023-11-29 08:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0005_remove_category_start_date_category_minimum_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='discount',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='category',
            name='end_date',
            field=models.DateField(default=datetime.datetime(2024, 11, 28, 14, 11, 32, 185161)),
        ),
    ]
