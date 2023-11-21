# Generated by Django 4.2.7 on 2023-11-17 12:15

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('category', '0001_initial'),
        ('brand', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=200)),
                ('description', models.TextField(blank=True, max_length=500)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('max_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('offer_percentage', models.IntegerField(default=65)),
                ('images', models.ImageField(upload_to='photos/product')),
                ('stock', models.IntegerField(default=0)),
                ('is_available', models.BooleanField(default=True)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('modified_date', models.DateField(auto_now_add=True)),
                ('product_images2', models.ImageField(null=True, upload_to='photos/product')),
                ('product_images3', models.ImageField(null=True, upload_to='photos/product')),
                ('product_images4', models.ImageField(null=True, upload_to='photos/product')),
                ('product_images5', models.ImageField(null=True, upload_to='photos/product')),
                ('quantity', models.IntegerField(default=25)),
                ('soft_deleted', models.BooleanField(default=False)),
                ('brand', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brand.brand')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='category.category')),
            ],
        ),
        migrations.CreateModel(
            name='Variation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variation_category', models.CharField(choices=[('colour', 'Colour')], default='Colour', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('variation_value', models.CharField(default='Black', max_length=100)),
                ('created_date', models.DateTimeField(auto_now=True)),
                ('stock', models.PositiveIntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductVariation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.product')),
                ('variation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.variation')),
            ],
        ),
    ]
