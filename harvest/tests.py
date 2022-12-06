import datetime
import decimal
import os
import random
from io import StringIO
from typing import Union

from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.test.utils import setup_test_environment
from django.urls import reverse, resolve
from django.conf import settings

from . import views
from .models import Harvest
from .forms import HarvestForm


def create_dummy_harvests(harvests_data: Union[dict, list[dict]]) -> None:
    """

    :param harvests_data: dict or list of dicts like {"owner": User, "number_of_harvests": int, "fruit": str, "year": int}
    :return: None
    """

    def _gen_date(year: int, dates_used: list[datetime.date]) -> datetime.date:
        g_date = datetime.date(year=year,
                               month=random.randint(5, 9),
                               day=random.randint(1, 30))
        if g_date in dates_used:
            return _gen_date(year, dates_used)
        else:
            return g_date


    if not isinstance(harvests_data, list):
        harvests_data = [harvests_data]
    dates_used = []
    for h_data in harvests_data:
        for _ in range(h_data['number_of_harvests']):
            date = _gen_date(year=h_data['year'], dates_used=dates_used)
            dates_used.append(date)
            Harvest.objects.create(owner=h_data['owner'],
                                   amount=random.randint(100, 1000),
                                   price=decimal.Decimal.from_float(0.5 + random.random() * 75),
                                   fruit=h_data['fruit'],
                                   date=date)


class UrlsTests(TestCase):
    """Tests for url routes"""

    def test_urls_resolve(self):
        self.assertEqual(resolve(reverse("harvest:home")).func, views.index)
        self.assertEqual(resolve(reverse("harvest:harvest-list")).func, views.harvest_list)
        self.assertEqual(resolve(reverse("harvest:harvest-add")).func, views.harvest_add)
        self.assertEqual(resolve(reverse("harvest:harvest-edit", args=[1])).func, views.harvest_edit)
        self.assertEqual(resolve(reverse("harvest:harvest-delete", args=[1])).func, views.harvest_delete)


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

    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")

    def test_form_rejects_no_data(self):
        HarvestForm(owner=self.user, h_id=None, data={})
        self.assertRaises(KeyError)

    def test_form_rejects_fruit_outside_choice(self):
        form = HarvestForm(data={
            "date": datetime.date.today(),
            "fruit": "kasztan",
            "amount": 1000,
            "price": 1.5},
            owner=self.user)
        self.assertFalse(form.is_valid())

    def test_form_rejects_incomplete_data(self):
        form = HarvestForm(data={
            "date": datetime.date.today(),
            "fruit": "apple",
            "amount": 1000,
            "price": 1.5,
        }, owner=self.user)
        self.assertTrue(form.is_valid())

    def test_form_accepts_correct_data(self):
        form = HarvestForm(data={
            "date": datetime.date.today(),
            "fruit": "apple",
            "amount": 1000,
            "price": 1.5,
        }, owner=self.user)
        self.assertTrue(form.is_valid())

    def test_form_rejects_amount_out_of_bounds(self):
        form = HarvestForm(data={
            "date": datetime.date.today(),
            "fruit": "apple",
            "amount": 10000000,
            "price": 1.5,
        }, owner=self.user)
        self.assertFalse(form.is_valid())

        form = HarvestForm(data={
            "date": datetime.date.today(),
            "fruit": "apple",
            "amount": 1000,
            "price": 1.546875,
        }, owner=self.user)
        self.assertFalse(form.is_valid())

        form = HarvestForm(data={
            "date": datetime.date.today(),
            "fruit": "apple",
            "amount": 1000,
            "price": 1111.1,
        }, owner=self.user)
        self.assertFalse(form.is_valid())


class IndexViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")
        create_dummy_harvests(harvests_data=[{
            "owner": self.user,
            "number_of_harvests": 7,
            "fruit": "raspberry",
            "year": 2022
        }, {
            "owner": self.user,
            "number_of_harvests": 5,
            "fruit": "cherry",
            "year": 2022
        }, {
            "owner": self.user,
            "number_of_harvests": 3,
            "fruit": "strawberry",
            "year": 2022
        }])

    def test_unauthenticated_not_shown_details(self):
        response = self.client.get(reverse("harvest:home"))
        self.assertTemplateUsed(response, "harvest/index.html")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Hello")
        self.assertNotContains(response, "Summary")

    def test_authenticated_shown_details(self):
        self.client.login(username="testeruser", password="testeruserpass")
        response = self.client.get(reverse("harvest:home"))
        self.assertTemplateUsed(response, "harvest/index.html")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Hello")
        self.assertContains(response, "Summary")
        self.assertEquals(response.context[0]['season_summary']['n_harvests'], 15)


class HarvestAddViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")
        Harvest.objects.create(date=datetime.date.today(),
                               fruit="cherry",
                               owner=self.user,
                               price=10,
                               amount=100)

    def test_unauthenticated_has_no_access(self):
        response = self.client.get(reverse("harvest:harvest-add"))

        self.assertTrue("login" in response.url)
        self.assertEquals(response.status_code, 302)

    def test_authenticated_user_has_access(self):
        self.client.login(username="testeruser", password="testeruserpass")
        response = self.client.get(reverse("harvest:harvest-add"))

        self.assertEquals(response.status_code, 200)

    def test_authenticated_user_creates_harvest(self):
        self.client.login(username="testeruser", password="testeruserpass")
        response = self.client.post(reverse("harvest:harvest-add"), data={
            "date": datetime.date.today(),
            "fruit": "strawberry",
            "amount": 100,
            "price": 10
        })

        self.assertEquals(response.status_code, 301)
        self.assertTrue("harvest/list" in response.url)
        self.assertTemplateUsed("harvest/add")

    def test_authenticated_user_creates_harvest_duplicate_rejected(self):
        self.client.login(username="testeruser", password="testeruserpass")
        response = self.client.post(reverse("harvest:harvest-add"), data={
            "date": datetime.date.today(),
            "fruit": "cherry",
            "amount": 100,
            "price": 10
        })

        self.assertContains(response, "already exists")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed("harvest/add")

    def test_authenticated_user_creates_harvest_bad_data(self):
        self.client.login(username="testeruser", password="testeruserpass")
        response = self.client.post(reverse("harvest:harvest-add"), data={
            "date": datetime.date(1900, 1, 1),
            "fruit": "cherry",
            "amount": 10000000,
            "price": 100
        })

        self.assertContains(response, "2 digits")
        self.assertContains(response, "higher than 5000")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed("harvest/add")

    def test_authenticated_user_creates_harvest_empty_data(self):
        self.client.login(username="testeruser", password="testeruserpass")
        response = self.client.post(reverse("harvest:harvest-add"), data={})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(Harvest.objects.all()), 1)
        self.assertTemplateUsed("harvest/add")


class HarvestEditViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")
        self.user2 = User.objects.create_user(username="testeruser2", password="testeruserpass2")
        self.test_harvest = Harvest(fruit="cherry",
                               date=datetime.date.today(),
                               amount=222,
                               price=10,
                               owner=self.user)
        self.test_harvest.save()
        self.test_harvest2 = Harvest(fruit="strawberry",
                                    date=datetime.date.today(),
                                    amount=222,
                                    price=10,
                                    owner=self.user)
        self.test_harvest2.save()

    def test_unauthenticated_has_no_access(self):
        response = self.client.get(f"/harvest/edit/{self.test_harvest.pk}")
        self.assertEquals(response.status_code, 302)
        self.assertTrue("login" in response.url)

    def test_user_is_not_an_owner(self):
        self.client.login(username="testeruser2", password="testeruserpass2")
        response = self.client.get(f"/harvest/edit/{self.test_harvest.pk}")
        self.assertEquals(response.status_code, 404)

    def test_harvest_not_existing(self):
        self.client.login(username="testeruser2", password="testeruserpass2")
        response = self.client.get(f"/harvest/edit/7")
        self.assertEquals(response.status_code, 404)

    def test_harvest_exists_correct_initial_data_from_get(self):
        self.client.login(username="testeruser", password="testeruserpass")
        response = self.client.get(f"/harvest/edit/{self.test_harvest.id}")
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "Cherry")

    def test_harvest_edit_post_correct_data(self):
        self.client.login(username="testeruser", password="testeruserpass")
        start_harvest_count = Harvest.objects.count()
        response = self.client.post(path=f"/harvest/edit/{self.test_harvest.id}",
                                    data={
                                        "date": self.test_harvest.date,
                                        "price": 7,
                                        "fruit": self.test_harvest.fruit,
                                        "amount": 327
                                    })
        harvests = Harvest.objects.all()
        self.assertEquals(response.status_code, 301)
        self.assertEquals(start_harvest_count, len(harvests))
        self.assertEquals(harvests[0].price, 7)
        self.assertEquals(harvests[0].amount, 327)

    def test_harvest_edit_post_duplicate_detected(self):
        self.client.login(username="testeruser", password="testeruserpass")
        start_harvest_count = Harvest.objects.count()
        response = self.client.post(path=f"/harvest/edit/{self.test_harvest2.id}",
                                    data={
                                        "date": self.test_harvest.date,
                                        "price": self.test_harvest.price,
                                        "fruit": self.test_harvest.fruit,
                                        "amount": self.test_harvest.amount
                                    })
        harvests = Harvest.objects.all()
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "already exists")
        self.assertEquals(start_harvest_count, len(harvests))

    def test_harvest_edit_post_invalid_data(self):
        self.client.login(username="testeruser", password="testeruserpass")
        start_harvest_count = Harvest.objects.count()
        response = self.client.post(path=f"/harvest/edit/{self.test_harvest2.id}",
                                    data={
                                        "date": datetime.date(1987, 10, 12),
                                        "price": 10000,
                                        "fruit": "raspberry",
                                        "amount": 10000,
                                    })

        harvests = Harvest.objects.all()
        self.assertContains(response, "4 digits")
        self.assertContains(response, "higher than 5000")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(start_harvest_count, len(harvests))

    def test_harvest_edit_post_invalid_date(self):
        self.client.login(username="testeruser", password="testeruserpass")
        start_harvest_count = Harvest.objects.count()
        response = self.client.post(path=f"/harvest/edit/{self.test_harvest2.id}",
                                    data={
                                        "date": datetime.date(1987, 10, 12),
                                        "price": 10,
                                        "fruit": "raspberry",
                                        "amount": 100,
                                    })

        harvests = Harvest.objects.all()
        self.assertContains(response, "Earliest")
        self.assertEquals(response.status_code, 200)
        self.assertEquals(start_harvest_count, len(harvests))

    def test_harvest_edit_incomplete_data(self):
        self.client.login(username="testeruser", password="testeruserpass")
        start_harvest_count = Harvest.objects.count()
        response = self.client.post(path=f"/harvest/edit/{self.test_harvest2.id}",
                                    data={
                                        "date": datetime.date(2018, 10, 12),
                                        "amount": 1000000,
                                    })

        harvests = Harvest.objects.all()
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, "be empty")
        self.assertEquals(start_harvest_count, len(harvests))


class HarvestDeleteViewTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")
        self.user2 = User.objects.create_user(username="testeruser2", password="testeruserpass2")
        self.test_harvest = Harvest(fruit="cherry",
                                    date=datetime.date.today(),
                                    amount=222,
                                    price=10,
                                    owner=self.user)
        self.test_harvest.save()

    def test_unauthenticated_has_no_access(self):
        response = self.client.post(path=f"/harvest/delete/{self.test_harvest.pk}")
        self.assertEquals(response.status_code, 302)

    def test_not_owner_gets_404(self):
        self.client.login(username="testeruser2", password="testeruserpass2")
        response = self.client.post(path=f"/harvest/delete/{self.test_harvest.pk}")
        self.assertEquals(response.status_code, 404)

    def test_owner_can_delete(self):
        self.client.login(username="testeruser", password="testeruserpass")
        response = self.client.post(path=f"/harvest/delete/{self.test_harvest.pk}")
        harvests = Harvest.objects.all()
        self.assertEquals(response.status_code, 301)
        self.assertEquals(len(harvests), 0)

    def test_harvest_not_exists_404(self):
        self.client.login(username="testeruser", password="testeruserpass")
        response = self.client.post(path=f"/harvest/delete/{2}")
        self.assertEquals(response.status_code, 404)


class HarvestListViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")
        self.test_harvest = Harvest(fruit="cherry",
                                    date=datetime.date.today(),
                                    amount=222,
                                    price=10,
                                    owner=self.user)
        self.test_harvest.save()

        self.test_harvest2 = Harvest(fruit="apple",
                                    date=datetime.date.today(),
                                    amount=222,
                                    price=10,
                                    owner=self.user)
        self.test_harvest2.save()

        self.test_harvest3 = Harvest(fruit="strawberry",
                                    date=datetime.date.today(),
                                    amount=222,
                                    price=10,
                                    owner=self.user)
        self.test_harvest3.save()

    def test_unauthenticated_has_no_access(self):
        response = self.client.get(path=f"/harvest/list/")
        self.assertEquals(response.status_code, 302)

    def test_logged_in_has_access(self):
        self.client.login(username="testeruser", password="testeruserpass",)
        response = self.client.get(path=f"/harvest/list/")
        self.assertEquals(response.status_code, 200)

    def test_harvests_per_page(self):
        self.client.login(username="testeruser", password="testeruserpass", )
        response = self.client.get(path=f"/harvest/list/?harvests-per-page=1")
        self.assertEquals(len(response.context[0]['harvests']), 1)

    def test_fruit_query_parameter(self):
        self.client.login(username="testeruser", password="testeruserpass", )
        response = self.client.get(path=f"/harvest/list/?harvests-per-page=3&fruit=cherry")
        self.assertEquals(len(response.context[0]['harvests']), 1)
        self.assertEquals(response.context[0]['harvests'][0].fruit, "cherry")

    def test_fruit_not_existing(self):
        self.client.login(username="testeruser", password="testeruserpass", )
        response = self.client.get(path=f"/harvest/list/?harvests-per-page=3&fruit=kasztan")
        self.assertEquals(len(response.context[0]['harvests']), 0)


class CustomCommandDeleteHarvestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")
        create_dummy_harvests({"owner": self.user,
                               "year": 2022,
                               "fruit": "raspberry",
                               "number_of_harvests": 6})

    def test_harvest_id_not_existing(self):
        out = StringIO()
        args = [777]
        call_command("delete_harvest", *args, stdout=out)
        self.assertIn(f"Harvest with id {777} does not exist", out.getvalue())

    def test_harvest_deleted_successfully(self):
        out = StringIO()
        args = [1]
        harvest = Harvest.objects.get(pk=1)
        harvests_count = Harvest.objects.count()
        call_command("delete_harvest", *args, stdout=out)
        self.assertIn(f"Harvest {harvest} successfully deleted", out.getvalue())
        self.assertEquals(harvests_count-1, Harvest.objects.count())


class CustomCommandDeleteUserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")
        create_dummy_harvests({"owner": self.user,
                               "year": 2022,
                               "fruit": "raspberry",
                               "number_of_harvests": 6})

    def test_user_id_not_existing(self):
        out = StringIO()
        args = [3]
        call_command("delete_user", *args, stdout=out)
        self.assertIn("User with given id does not exist", out.getvalue())

    def test_user_correctly_deleted(self):
        out = StringIO()
        args = [1]
        call_command("delete_user", *args, stdout=out)
        harvests_count = Harvest.objects.count()
        self.assertIn(f"User {self.user.username} successfully deleted", out.getvalue())
        self.assertEquals(harvests_count, 0)


class CustomCommandGenCsvTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")
        create_dummy_harvests({"owner": self.user,
                               "year": 2022,
                               "fruit": "raspberry",
                               "number_of_harvests": 6})

    def test_file_created(self):
        out = StringIO()

        opts = {"test": 1}

        filename = f"test_harvests_{datetime.date.today()}.csv"
        filepath = settings.BASE_DIR / "csv_out" / filename

        call_command("gen_csv", stdout=out, **opts)
        self.assertIn(filename, out.getvalue())
        self.assertTrue(os.path.exists(filepath))

        if os.path.exists(filepath):
            os.remove(filepath)

    def test_options_in_filename(self):
        out = StringIO()

        opts = {"test": 1,
                "user_id": self.user.pk,
                "fruit": "raspberry",
                "year": 2022}

        filename = f"test_harvests_{self.user.pk}_raspberry_2022_{datetime.date.today()}.csv"
        filepath = settings.BASE_DIR / "csv_out" / filename

        call_command("gen_csv", stdout=out, **opts)
        self.assertIn(filename, out.getvalue())
        self.assertTrue(os.path.exists(filepath))

        if os.path.exists(filepath):
            os.remove(filepath)

    def test_user_not_existing(self):
        out = StringIO()

        opts = {"test": 1,
                "user_id": 777}

        call_command("gen_csv", stdout=out, **opts)
        self.assertIn(f"User with given id ({777}) does not exist", out.getvalue())


class CustomCommandHarvestCountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")
        create_dummy_harvests({"owner": self.user,
                                "year": 2022,
                                "fruit": "raspberry",
                                "number_of_harvests": 6})

    def test_harvests_count_correct(self):
        hc = Harvest.objects.count()
        out = StringIO()
        call_command("harvest_count", stdout=out)
        self.assertIn(str(hc), out.getvalue())


class CustomCommandListUserHarvestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")
        self.user2 = User.objects.create_user(username="testeruser2", password="testeruserpass2")
        create_dummy_harvests([{"owner": self.user,
                               "year": 2022,
                               "fruit": "raspberry",
                               "number_of_harvests": 6},
                              {"owner": self.user,
                               "year": 2021,
                               "fruit": "cherry",
                               "number_of_harvests": 3},
                              {"owner": self.user,
                               "year": 2020,
                               "fruit": "apple",
                               "number_of_harvests": 3}])

    def test_list_user_harvests_user_doesnt_exist(self):
        out = StringIO()
        args = [3]
        call_command("list_user_harvest", *args, stdout=out)
        self.assertIn("User with given id does not exist", out.getvalue())

    def test_list_user_harvests_user_has_no_harvests(self):
        out = StringIO()
        args = [2]
        call_command("list_user_harvest", *args, stdout=out)
        self.assertIn("There are no Harvests for given user", out.getvalue())

    def test_list_user_harvests_user_exists(self):
        out = StringIO()
        args = [1]
        call_command("list_user_harvest", *args, stdout=out)
        self.assertIn("testeruser has 12 Harvests with specified parameters", out.getvalue())
        self.assertIn("raspberry", out.getvalue())
        self.assertIn("apple", out.getvalue())
        self.assertIn("cherry", out.getvalue())

    def test_list_user_harvests_filter_by_year(self):
        out = StringIO()
        args = [1]
        options = {"year": 2022}
        call_command("list_user_harvest", *args, **options, stdout=out)
        self.assertIn("testeruser has 6 Harvests", out.getvalue())
        self.assertIn("raspberry", out.getvalue())
        self.assertNotIn("cherry", out.getvalue())
        self.assertNotIn("apple", out.getvalue())
        self.assertNotIn("strawberry", out.getvalue())

    def test_list_user_harvests_filter_by_fruit(self):
        out = StringIO()
        args = [1]
        options = {"fruit": "cherry"}
        call_command("list_user_harvest", *args, **options, stdout=out)
        self.assertIn("testeruser has 3 Harvests", out.getvalue())
        self.assertIn("cherry", out.getvalue())
        self.assertNotIn("apple", out.getvalue())
        self.assertNotIn("raspberry", out.getvalue())
        self.assertNotIn("strawberry", out.getvalue())

    def test_list_user_harvests_filter_by_fruit_not_found(self):
        out = StringIO()
        args = [1]
        options = {"fruit": "strawberry"}
        call_command("list_user_harvest", *args, **options, stdout=out)
        self.assertIn("Given user has no harvests with specified parameters", out.getvalue())
        self.assertNotIn("cherry", out.getvalue())
        self.assertNotIn("apple", out.getvalue())
        self.assertNotIn("raspberry", out.getvalue())
        self.assertNotIn("strawberry", out.getvalue())

    def test_list_user_harvests_filter_by_year_not_found(self):
        out = StringIO()
        args = [1]
        options = {"year": 1999}
        call_command("list_user_harvest", *args, **options, stdout=out)
        self.assertIn("Given user has no harvests with specified parameters", out.getvalue())
        self.assertNotIn("cherry", out.getvalue())
        self.assertNotIn("apple", out.getvalue())
        self.assertNotIn("raspberry", out.getvalue())
        self.assertNotIn("strawberry", out.getvalue())


class CustomCommandListUsersTests(TestCase):
    def test_list_users_no_users_existing(self):
        out = StringIO()
        call_command("list_users", stdout=out)
        self.assertIn('no registered', out.getvalue())

    def test_list_users_correct(self):
        user = User.objects.create_user(username="testeruser", password="testeruserpass")
        user2 = User.objects.create_user(username="testeruser2", password="testeruserpass2")
        create_dummy_harvests([{"owner": user, "year": 2022,
                                "fruit": "raspberry",
                                "number_of_harvests": 3},
                               {"owner": user2, "year": 2022,
                                "fruit": "raspberry",
                                "number_of_harvests": 7}
                               ])
        out = StringIO()
        call_command("list_users", stdout=out)
        self.assertIn("testeruser", out.getvalue())
        self.assertIn("testeruser2", out.getvalue())
        self.assertIn("Registered users: 2", out.getvalue())
        self.assertIn("3", out.getvalue())
        self.assertIn("7", out.getvalue())

