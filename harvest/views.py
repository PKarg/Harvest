import traceback

from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import CustomSignupForm, HarvestForm
from .models import Harvest

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
    form = HarvestForm()

    if request.method == "POST":
        form = HarvestForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse("harvest:harvest-list"))

    return render(request,
                  template_name="harvest/harvest_add.html",
                  context={"form": form})


@login_required
def harvest_edit(request: HttpRequest, pk: int):
    """View for editing data of specific harvest"""
    harvest = get_object_or_404(Harvest, id=pk)
    form = HarvestForm(instance=harvest)

    if request.method == "POST":
        form = HarvestForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            harvest.date = data.get("date")
            harvest.price = data.get("price")
            harvest.fruit = data.get("fruit")
            harvest.amount = data.get("amount")
            harvest.save()
            return redirect(reverse("harvest:harvest-list"))

    return render(request,
                  template_name="harvest/harvest_edit.html",
                  context={"form": form, "harvest": harvest})


@login_required
def harvest_delete(request: HttpRequest):
    """View for deleting specified harvest"""
    # TODO implement
    return HttpResponse("Harvest delete")
