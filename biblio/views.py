from django.shortcuts import redirect

from .handle_views.user import handle_user_get


def user(request):
    if request.method == "POST":
        return handle_user_post(request)

    return handle_user_get(request)


def main_index(request):
    return redirect('books:stats')
