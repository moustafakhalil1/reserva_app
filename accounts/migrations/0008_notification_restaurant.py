# Generated by Django 4.2.13 on 2024-05-24 12:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='accounts.restaurant'),
        ),
    ]
