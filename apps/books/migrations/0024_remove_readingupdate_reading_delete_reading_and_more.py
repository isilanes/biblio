# Modified by hand on 2022-12-28 17:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0023_remove_reading_book'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='readingupdate',
                    name='reading',
                ),
                migrations.DeleteModel(
                    name='Reading',
                ),
                migrations.DeleteModel(
                    name='ReadingUpdate',
                ),
            ],
            database_operations=[]  # do nothing
        )
    ]
