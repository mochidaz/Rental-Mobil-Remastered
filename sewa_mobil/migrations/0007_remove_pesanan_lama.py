# Generated by Django 3.0.8 on 2020-10-14 14:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sewa_mobil', '0006_auto_20201014_1125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pesanan',
            name='lama',
        ),
    ]
