# Generated by Django 3.1.3 on 2020-11-16 16:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0014_delete_bookendevent'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BookStartEvent',
        ),
    ]