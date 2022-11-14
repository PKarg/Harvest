from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest):
    # TODO implement
    return HttpResponse("Home")


def sign_up(request: HttpRequest):
    # TODO implement
    return HttpResponse("Sign up")


def harvest_list(request: HttpRequest):
    # TODO implement
    return HttpResponse("Harvest list")


def harvest_add(request: HttpRequest):
    # TODO implement
    return HttpResponse("Harvest add")


def harvest_edit(request: HttpRequest):
    # TODO implement
    return HttpResponse("Harvest edit")


def harvest_delete(request: HttpRequest):
    # TODO implement
    return HttpResponse("Harvest delete")
