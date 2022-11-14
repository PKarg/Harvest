from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import CustomSignupForm


def index(request: HttpRequest):
    """Homepage view displaying seasonal summary and 5 last harvests"""
    # TODO implement
    return HttpResponse("Home")


def sign_up(request: HttpRequest):
    """View for creating new user accounts"""
    if request.method == 'POST':
        error_msg = None
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("login"))
    else:
        form = CustomSignupForm()
        error_msg = None
    return render(request, "registration/signup.html",
                  context={
                      "form": form,
                      "error_msg": error_msg
                  })


@login_required
def harvest_list(request: HttpRequest):
    """View for listing user harvests with pagination and filtering by year and fruit"""
    # TODO implement
    return HttpResponse("Harvest list")


@login_required
def harvest_add(request: HttpRequest):
    """View for adding new harvests"""
    # TODO implement
    return HttpResponse("Harvest add")


@login_required
def harvest_edit(request: HttpRequest):
    """View for editing data of specific harvest"""
    # TODO implement
    return HttpResponse("Harvest edit")


@login_required
def harvest_delete(request: HttpRequest):
    """View for deleting specified harvest"""
    # TODO implement
    return HttpResponse("Harvest delete")
