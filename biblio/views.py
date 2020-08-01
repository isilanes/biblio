from django.shortcuts import render, redirect


def user(request):
    return render(request, "user.html", {})


def main_index(request):
    return redirect('books:stats')
