# Generated by Django 2.1.3 on 2018-12-22 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0006_book_owned'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='owned',
            field=models.BooleanField(default=True, verbose_name='Owned'),
        ),
    ]
