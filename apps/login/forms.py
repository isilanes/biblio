from django import forms
from django.contrib.auth.models import User


class MyUserCreationForm(forms.Form):
    username = forms.CharField(
        label="User name",
        help_text="No spaces and lowercase",
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
        help_text=None,
    )
    password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput,
        strip=False,
        help_text="Re-introduce the same password, to verify it.",
    )
    email = forms.EmailField(label="e-mail")

    def is_valid(self):
        """Perform default validation, plus some extra custom ones (such as matching passwords)."""

        # Fail if default check fails:
        if not super(forms.Form, self).is_valid():
            return False

        # Fail if empty password or confirmation does not match:
        pw1 = self.cleaned_data["password1"]
        pw2 = self.cleaned_data["password2"]

        if pw1 != pw2:
            self.add_error('password2', "Passwords do not coincide.")
            return False

        # Fail if username or e-mail already taken:
        if User.objects.filter(username=self.cleaned_data["username"]).exists():
            self.add_error('username', "User name already exists.")
            return False

        if User.objects.filter(email=self.cleaned_data["email"]).exists():
            self.add_error('email', "User with that e-mail address already exists.")
            return False

        return True

    def save(self):
        """
        Save a user with info in this form.
        Return created user.
        """
        data = self.cleaned_data
        new_user = User(
            username=data["username"],
            email=data["email"],
        )
        new_user.set_password(data["password1"])
        new_user.save()

        return new_user
