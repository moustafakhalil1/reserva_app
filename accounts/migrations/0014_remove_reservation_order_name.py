# Generated by Django 4.2.13 on 2024-05-30 19:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_reservation_order_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='order_name',
        ),
    ]
