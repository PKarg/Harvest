import datetime
import decimal

from django.db import IntegrityError
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.test.utils import setup_test_environment
from django.urls import reverse, resolve

from . import views
from .models import Harvest
from .forms import HarvestForm


class UrlsTests(TestCase):
    """Tests for url routes"""

    def test_urls_resolve(self):
        self.assertEqual(resolve(reverse("harvest:home")).func, views.index)
        self.assertEqual(resolve(reverse("harvest:harvest-list")).func, views.harvest_list)
        self.assertEqual(resolve(reverse("harvest:harvest-add")).func, views.harvest_add)
        self.assertEqual(resolve(reverse("harvest:harvest-edit")).func, views.harvest_edit)
        self.assertEqual(resolve(reverse("harvest:harvest-delete")).func, views.harvest_delete)


class HarvestTests(TestCase):
    """Tests for Harvest model"""

    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")

    def test_create_harvest_correct(self):
        test_harvest = Harvest(fruit="raspberry",
                               date=datetime.date.today(),
                               amount=777,
                               price=77,
                               owner=self.user)

        test_harvest.save()
        harvests = Harvest.objects.all()
        self.assertTrue(harvests)

    def test_duplicate_raises_integrity_error(self):
        test_harvest1 = Harvest(fruit="raspberry",
                                date=datetime.date.today(),
                                amount=777,
                                price=77,
                                owner=self.user)

        test_harvest2 = Harvest(fruit="raspberry",
                                date=datetime.date.today(),
                                amount=777,
                                price=77,
                                owner=self.user)

        with self.assertRaises(IntegrityError) as test_context:
            test_harvest1.save()
            test_harvest2.save()

        self.assertTrue("UNIQUE constraint failed" in str(test_context.exception))

    def test_create_harvest_missing_data_raises_integrity_error(self):
        test_harvest = Harvest(fruit="cherry",
                               date=datetime.date.today(),
                               amount=222,
                               owner=self.user)

        with self.assertRaises(IntegrityError) as test_context:
            test_harvest.save()

        self.assertTrue("NOT NULL constraint failed" in str(test_context.exception))

    def test_create_harvest_values_out_of_bounds_raises_integrity_error(self):
        test_harvest = Harvest(fruit="cherry",
                               date=datetime.date.today(),
                               amount=222,
                               price=1000,
                               owner=self.user)

        with self.assertRaises(decimal.InvalidOperation) as test_context:
            test_harvest.save()

        self.assertTrue("InvalidOperation" in str(test_context.exception))

    def test_edit_harvest_correct(self):
        test_harvest = Harvest(fruit="cherry",
                               date=datetime.date.today(),
                               amount=222,
                               price=10,
                               owner=self.user)
        test_harvest.save()

        test_harvest_edit = Harvest.objects.get(pk=1)
        test_harvest_edit.fruit = "raspberry"
        test_harvest_edit.save()
        harvest_in_db = Harvest.objects.get(pk=1)
        self.assertTrue(harvest_in_db.fruit == "raspberry")

    def test_edit_harvest_duplicate_raises_exception(self):
        test_harvest1 = Harvest(fruit="cherry",
                                date=datetime.date.today(),
                                amount=222,
                                price=10,
                                owner=self.user)
        test_harvest1.save()

        test_harvest2 = Harvest(fruit="raspberry",
                                date=datetime.date.today(),
                                amount=222,
                                price=12,
                                owner=self.user)
        test_harvest2.save()
        test_harvest2_edit = Harvest.objects.get(pk=2)
        test_harvest2_edit.fruit = "cherry"

        with self.assertRaises(IntegrityError) as test_context:
            test_harvest2_edit.save()

        self.assertTrue("UNIQUE constraint failed", str(test_context.exception))

    def test_harvest_value_property_correct(self):
        test_harvest1 = Harvest(fruit="cherry",
                                date=datetime.date.today(),
                                amount=222,
                                price=10,
                                owner=self.user)
        self.assertEqual(2220, test_harvest1.value)


class HarvestFormTests(TestCase):

    def test_form_rejects_no_data(self):
        form = HarvestForm(data={})
        self.assertRaises(KeyError)

    def test_form_rejects_fruit_outside_choice(self):
        form = HarvestForm(data={
            "date": datetime.date.today(),
            "fruit": "kasztan",
            "amount": 1000,
            "price": 1.5,})
        self.assertFalse(form.is_valid())

    def test_form_rejects_incomplete_data(self):
        form = HarvestForm(data={
            "date": datetime.date.today(),
            "fruit": "apple",
            "amount": 1000,
            "price": 1.5,
        })
        self.assertTrue(form.is_valid())

    def test_form_accepts_correct_data(self):
        form = HarvestForm(data={
            "date": datetime.date.today(),
            "fruit": "apple",
            "amount": 1000,
            "price": 1.5,
        })
        self.assertTrue(form.is_valid())

    def test_form_rejects_amount_out_of_bounds(self):
        form = HarvestForm(data={
            "date": datetime.date.today(),
            "fruit": "apple",
            "amount": 10000000,
            "price": 1.5,
        })
        self.assertFalse(form.is_valid())

        form = HarvestForm(data={
            "date": datetime.date.today(),
            "fruit": "apple",
            "amount": 1000,
            "price": 1.546875,
        })
        self.assertFalse(form.is_valid())

        form = HarvestForm(data={
            "date": datetime.date.today(),
            "fruit": "apple",
            "amount": 1000,
            "price": 1111.1,
        })
        self.assertFalse(form.is_valid())


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
