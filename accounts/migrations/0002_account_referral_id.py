# Generated by Django 4.2.7 on 2023-12-01 09:34

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='referral_id',
            field=models.UUIDField(blank=True, default=uuid.uuid4, null=True, unique=True),
        ),
    ]
