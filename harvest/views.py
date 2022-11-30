import datetime
import traceback

from django.core.paginator import Paginator
from django.db.models.functions import ExtractYear
from django.http import HttpRequest, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import CustomSignupForm, HarvestForm
from .models import Harvest


def index(request: HttpRequest):
    """Homepage view displaying seasonal summary and 5 last harvests"""
    # TODO implement
    # 5 recent harvests
    context = {"date": datetime.date.today()}

    if request.user.is_authenticated:
        season = request.GET.get(key="season", default=datetime.date.today().year)

        seasons = Harvest.objects.filter(owner=request.user)\
            .annotate(year=ExtractYear('date')).values('year')

        seasons = set([s['year'] for s in seasons])

        recent_harvests = Harvest.objects.filter(owner=request.user).order_by("date").all()[:5]

        # dict with season summary:
        all_harvests = Harvest.objects.filter(date__gte=datetime.date(year=season, month=1, day=1),
                                              owner=request.user).all()

        harvested_by_fruit = {}
        for h in all_harvests:
            if not harvested_by_fruit.get(h.fruit):
                harvested_by_fruit[h.fruit] = [h.amount, h.profits]
            else:
                harvested_by_fruit[h.fruit][0] += h.amount
                harvested_by_fruit[h.fruit][1] += h.profits

        season_summary = {
            "n_harvests": len(all_harvests),
            "fruit_summary": harvested_by_fruit,
        }

        context['chosen_season'] = season
        context['recent_harvests'] = recent_harvests
        context['season_summary'] = season_summary
        context['seasons'] = seasons

    return render(request,
                  template_name="harvest/index.html",
                  context=context)


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
    harvests = Harvest.objects.filter(owner=request.user)
    fruit = request.GET.get(key="fruit")

    if fruit and fruit != "all":
        harvests = harvests.filter(fruit=fruit)

    harvests_n = len(harvests)
    limit = int(request.GET.get(key="harvests-per-page", default=5))

    paginator = Paginator(harvests, per_page=limit)
    page_number = request.GET.get(key="page", default=1)
    page_obj = paginator.get_page(page_number)

    fields = {"fruit": "Fruit",
              "date": "Date",
              "amount": "Harvested",
              "price": "Price",
              "profits": "Profits"}

    return render(request,
                  template_name="harvest/harvest_list.html",
                  context={
                      "fields": fields,
                      "limit": limit,
                      "fruit": fruit,
                      "user": request.user,
                      "harvests_n": harvests_n,
                      "page_obj": page_obj,
                      "harvests": page_obj.object_list
                  })


@login_required
def harvest_add(request: HttpRequest):
    """View for adding new harvests"""
    form = HarvestForm(request.user)

    if request.method == "POST":
        form = HarvestForm(request.user, None, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            harvest = Harvest(owner=form.owner, fruit=data['fruit'],
                              date=data['date'], amount=data['amount'],
                              price=data['price'])
            harvest.save()
            return redirect(reverse("harvest:harvest-list"), permanent=True)

    return render(request,
                  template_name="harvest/harvest_add.html",
                  context={"form": form})


@login_required
def harvest_edit(request: HttpRequest, pk: int):
    """View for editing data of specific harvest"""
    harvest = Harvest.objects.filter(pk=pk).filter(owner=request.user).first()
    if not harvest:
        raise Http404("Harvest not found")

    form = HarvestForm(instance=harvest, owner=harvest.owner)
    if request.method == "POST":
        form = HarvestForm(request.user, pk, request.POST)

        if form.is_valid():
            data = form.cleaned_data
            harvest.date = data.get("date")
            harvest.price = data.get("price")
            harvest.fruit = data.get("fruit")
            harvest.amount = data.get("amount")
            harvest.owner = form.owner
            harvest.save()
            return redirect(reverse("harvest:harvest-list"), permanent=True)

    return render(request,
                  template_name="harvest/harvest_edit.html",
                  context={"form": form, "harvest": harvest})


@login_required
def harvest_delete(request: HttpRequest, pk: int):
    """View for deleting specified harvest"""
    harvest = Harvest.objects.filter(pk=pk).filter(owner=request.user).first()
    if not harvest:
        raise Http404("Harvest not found")

    if request.method == "POST":
        harvest.delete()
        return redirect(reverse("harvest:harvest-list"), permanent=True)

    return render(request,
                  template_name="harvest/harvest_delete.html",
                  context={"harvest": harvest})
