# Generated by Django 4.2.7 on 2023-11-19 18:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='color',
            field=models.ForeignKey(max_length=50, on_delete=django.db.models.deletion.CASCADE, related_name='color_variation', to='product.variation'),
        ),
    ]