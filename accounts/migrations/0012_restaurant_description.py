# Generated by Django 4.2.13 on 2024-05-24 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_table_is_reserved_alter_reservation_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
