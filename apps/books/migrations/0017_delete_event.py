# Generated by Django 3.1.3 on 2020-11-16 16:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0016_delete_pageupdateevent'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Event',
        ),
    ]