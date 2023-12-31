# Generated by Django 4.2.7 on 2023-11-28 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_product_check_max_price_gt_price'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='product',
            name='check_max_price_gt_price',
        ),
        migrations.AddConstraint(
            model_name='product',
            constraint=models.CheckConstraint(check=models.Q(('max_price__gte', models.F('price'))), name='check_max_price_gte_price'),
        ),
    ]
