# Generated by Django 4.2.7 on 2023-11-25 07:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_coupon_maximum_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='valid_from',
        ),
    ]
