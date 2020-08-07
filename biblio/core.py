from .models import UserPreferences


def save_user_preferences(data, user):
    prefs = UserPreferences.objects.get(user=user)
    prefs.books_per_year = data["books_per_year"]
    prefs.pages_per_year = data["pages_per_year"]
    prefs.save()

