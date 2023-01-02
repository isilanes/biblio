from typing import Optional

from django.utils import timezone

from apps.readings.models import Reading, ReadingUpdate


def update_reading_progress(
    reading: Reading,
    pages: Optional[int] = None,
    percent: Optional[float] = None,
) -> None:
    """
    If a valid amount of pages, or read percent, is given, then update the
    Reading. This actually means to create a new ReadingUpdate object
    with te adequate amount of pages.

    Args:
        reading (Reading): Reading object to update.
        pages (int): if specified, amount of pages read.
        percent (float): if specified, percentage of book read.

    Returns:
        Nothing.
    """
    max_pages = reading.edition.pages
    new_pages = 0

    if percent is not None and percent <= 100:
        new_pages = int(percent * max_pages / 100)

    new_pages = max(pages, new_pages)

    if reading.page_progress < new_pages <= max_pages:  # only save if an update, and valid (less than max)
        ReadingUpdate(reading=reading, page=new_pages, date=timezone.now()).save()

