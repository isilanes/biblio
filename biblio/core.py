import time

from .models import UserPreferences


def save_user_preferences(data, user):
    try:
        prefs = UserPreferences.objects.get(user=user)
    except UserPreferences.DoesNotExist:  # create new, if it doesn't exist
        prefs = UserPreferences()
    prefs.books_per_year = data["books_per_year"]
    prefs.pages_per_year = data["pages_per_year"]
    prefs.save()


class TicToc:

    def __init__(self):
        self.t0 = None
        self.tic()

    def tic(self):
        self.t0 = time.time()

    def toc(self, msg=None):
        t1 = time.time()
        dt = (t1 - self.t0) * 1000
        print(f"{msg}: {dt:.1f} ms")
        self.t0 = t1

