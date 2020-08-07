from django.shortcuts import render

from biblio.models import UserPreferences
from biblio.forms import UserPreferencesForm


def handle_user_get(request):
    initial = {}
    prefs = UserPreferences.objects.filter(user=request.user).first()  # there should be 1 or 0
    if prefs is not None:
        initial = {
            "books_per_year": prefs.books_per_year,
            "pages_per_year": prefs.pages_per_year,
        }

    form = UserPreferencesForm(initial=initial)

    context = {
        "form": form,
    }

    return render(request, "user.html", context)
