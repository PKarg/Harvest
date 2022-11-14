from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest):
    """Homepage view displaying seasonal summary and 5 last harvests"""
    # TODO implement
    return HttpResponse("Home")


def sign_up(request: HttpRequest):
    """View for creating new user accounts"""
    # TODO implement
    return HttpResponse("Sign up")


def harvest_list(request: HttpRequest):
    """View for listing user harvests with pagination and filtering by year and fruit"""
    # TODO implement
    return HttpResponse("Harvest list")


def harvest_add(request: HttpRequest):
    """View for adding new harvests"""
    # TODO implement
    return HttpResponse("Harvest add")


def harvest_edit(request: HttpRequest):
    """View for editing data of specific harvest"""
    # TODO implement
    return HttpResponse("Harvest edit")


def harvest_delete(request: HttpRequest):
    """View for deleting specified harvest"""
    # TODO implement
    return HttpResponse("Harvest delete")
