# Generated by Django 3.2.1 on 2023-10-16 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_wallet_balance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='balance',
            field=models.IntegerField(default=0),
        ),
    ]
