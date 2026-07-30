from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, "core/home.html")


def about(request):
    return render(request, "core/about.html")


def projects(request):
    return render(request, "core/projects.html")


def notes(request):
    return render(request, "core/notes.html")


def contact(request):
    return render(request, "core/contact.html")
