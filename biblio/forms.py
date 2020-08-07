from django import forms
from django.contrib.auth.models import User

from . import core
from biblio.models import UserPreferences


class UserPreferencesForm(forms.ModelForm):

    class Meta:
        model = UserPreferences
        fields = ["books_per_year", "pages_per_year"]

    def save(self, pk):
        data = self.cleaned_data
        user = User.objects.get(pk=pk)
        core.save_user_preferences(data, user)
