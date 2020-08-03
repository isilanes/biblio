from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout, login

from .forms import MyUserCreationForm


def logout(request):
    """Log out user (if logged in)."""

    auth_logout(request)

    return redirect('main_index')


def signup(request):
    """Register a user."""

    if request.method == "POST":
        form = MyUserCreationForm(request.POST)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "login/signup.html", context)

        # Save new user in DB:
        new_user = form.save()

        # Log-in as newly-created user:
        login(request, user=new_user)

        return redirect("main_index")
    else:
        form = MyUserCreationForm()

        context = {
            "form": form,
        }

        return render(request, "login/signup.html", context)
