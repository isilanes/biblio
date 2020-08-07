from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .handle_views.user import handle_user_get, handle_user_post


@login_required
def user(request):
    if request.method == "POST":
        return handle_user_post(request)

    return handle_user_get(request)


@login_required
def main_index(request):
    return redirect('books:stats')
