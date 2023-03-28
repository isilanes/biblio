# Generated by Django 4.1.5 on 2023-03-28 21:17

from django.db import migrations, models

from apps.readings.lib.custom_definitions import ReadingStatus


def set_completed_status(apps, schema) -> None:
    """
    By default, all Readings will have status=STARTED. Set status=COMPLETED
    for the Readings that were completed (have an ending date).
    """
    readings_model = apps.get_model("readings", "Reading")
    finished_readings = readings_model.objects.filter(end__isnull=False)
    finished_readings.update(status=ReadingStatus.COMPLETED)


class Migration(migrations.Migration):

    dependencies = [
        ('readings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reading',
            name='status',
            field=models.PositiveSmallIntegerField(
                choices=[(1, 'STARTED'), (2, 'COMPLETED'), (3, 'DNF')],
                default=ReadingStatus['STARTED'],
            ),
        ),
        migrations.RunPython(
            code=set_completed_status,
            reverse_code=migrations.RunPython.noop,
        )
    ]
