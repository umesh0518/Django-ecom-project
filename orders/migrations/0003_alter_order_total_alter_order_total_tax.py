# Generated by Django 5.0.6 on 2024-07-20 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_remove_order_vendors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_tax',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
