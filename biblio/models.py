from django.db import models
from django.contrib.auth.models import User


class UserPreferences(models.Model):
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE, default=1)
    books_per_year = models.IntegerField("Books per year", default=1)
    pages_per_year = models.IntegerField("Pages per year", default=100)

    def __str__(self):
        return f"{self.user}"
