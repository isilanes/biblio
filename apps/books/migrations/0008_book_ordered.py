# Generated by Django 2.1.3 on 2019-01-01 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_auto_20181222_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='ordered',
            field=models.BooleanField(default=False, verbose_name='Ordered'),
        ),
    ]