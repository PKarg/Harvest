from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.test.utils import setup_test_environment
from django.urls import reverse

from . import views
from models import Harvest


class HarvestTests(TestCase):
    """Tests for Harvest model"""

    def setUp(self):
        # TODO create user to use in tests
        pass

    def test_create_harvest_correct(self):
        # TODO implement
        pass

    def test_duplicate_raises_exception(self):
        # TODO implement
        pass

    def test_create_harvest_missing_data(self):
        # TODO implement
        pass

    def test_create_harvest_values_out_of_bounds(self):
        # TODO implement
        pass

    def test_edit_harvest_correct(self):
        # TODO implement
        pass

    def test_edit_harvest_duplicate_raises_exception(self):
        # TODO implement
        pass


class IndexViewTests(TestCase):
    # TODO implement
    pass


class HarvestCreateViewTests(TestCase):
    # TODO implement
    pass


class HarvestEditViewTests(TestCase):
    # TODO implement
    pass


class HarvestDeleteViewTests(TestCase):
    # TODO implement
    pass


class CustomCommandDeleteHarvestTests(TestCase):
    # TODO implement
    pass


class CustomCommandDeleteUserTests(TestCase):
    # TODO implement
    pass


class CustomCommandGenCsvTests(TestCase):
    # TODO implement
    pass


class CustomCommandHarvestCountTests(TestCase):
    # TODO implement
    pass


class CustomCommandListUserHarvestTests(TestCase):
    # TODO implement
    pass


class CustomCommandListUsersTests(TestCase):
    # TODO implement
    pass


class CustomCommandUserCountTests(TestCase):
    # TODO implement
    pass
