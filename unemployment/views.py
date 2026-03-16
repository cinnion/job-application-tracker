from django.shortcuts import render, redirect, get_object_or_404


def homepage(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")
