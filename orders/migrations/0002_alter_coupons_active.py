# Generated by Django 3.2.1 on 2023-10-13 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupons',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
