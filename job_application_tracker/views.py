"""
Our views for the homepage and about page.
"""
from django.shortcuts import render


def home(request):
    """
    Our homepage.

    Args:
        request (HTTPRequest): Our request.

    Returns:
        Our HTTPResponse of the rendered home page.

    """
    return render(request, "home.html")


def about(request):
    """
    Our about page.

    Args:
        request (HTTPRequest): Our request.

    Returns:
        Our HTTPResponse of the rendered about page.

    """
    return render(request, "about.html")
