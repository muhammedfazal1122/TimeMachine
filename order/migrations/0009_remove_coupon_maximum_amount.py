# Generated by Django 4.2.7 on 2023-11-25 14:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_remove_coupon_valid_from'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='maximum_amount',
        ),
    ]
