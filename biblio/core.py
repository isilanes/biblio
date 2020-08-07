from .models import UserPreferences


def save_user_preferences(data, user):
    try:
        prefs = UserPreferences.objects.get(user=user)
    except UserPreferences.DoesNotExist:  # create new, if it doesn't exist
        prefs = UserPreferences()
    prefs.books_per_year = data["books_per_year"]
    prefs.pages_per_year = data["pages_per_year"]
    prefs.save()

