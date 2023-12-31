# Generated by Django 4.2.7 on 2023-11-28 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_remove_product_check_max_price_gt_price'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='product',
            constraint=models.CheckConstraint(check=models.Q(('max_price__gt', models.F('price'))), name='check_max_price_gt_price'),
        ),
    ]
