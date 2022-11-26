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
        self.assertEqual(resolve(reverse("harvest:harvest-edit", args=[1])).func, views.harvest_edit)
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

    def setUP(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")

    def test_form_rejects_no_data(self):
        form = HarvestForm(data={}, owner=self.user)
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
    # TODO implement
    pass

    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")


class HarvestAddViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")
        self.client = Client()

        Harvest.objects.create(date=datetime.date.today(),
                               fruit="cherry",
                               owner=self.user,
                               price=10,
                               amount=100)

    def test_unauthorized_has_no_access(self):
        response = self.client.get(reverse("harvest:harvest-add"))

        self.assertTrue("login" in response.url)
        self.assertEquals(response.status_code, 302)

    def test_authorized_user_has_access(self):
        self.client.login(username="testeruser", password="testeruserpass")
        response = self.client.get(reverse("harvest:harvest-add"))

        self.assertEquals(response.status_code, 200)

    def test_authorized_user_creates_harvest(self):
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

    def test_authorized_user_creates_harvest_duplicate_rejected(self):
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

    def test_authorized_user_creates_harvest_bad_data(self):
        self.client.login(username="testeruser", password="testeruserpass")
        response = self.client.post(reverse("harvest:harvest-add"), data={
            "date": datetime.date(1900, 1, 1),
            "fruit": "cherry",
            "amount": 10000000,
            "price": 100
        })

        self.assertContains(response, "Earliest accepted harvest year")
        self.assertContains(response, "2 digits")
        self.assertContains(response, "or equal to 5000")
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed("harvest/add")

    def test_authorized_user_creates_harvest_empty_data(self):
        self.client.login(username="testeruser", password="testeruserpass")
        with self.assertRaises(KeyError) as test_context:
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

    def test_unauthorized_has_no_access(self):
        response = self.client.get(f"/harvest/edit/{self.test_harvest.pk}")
        print(response.url)
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
        print(response.content)
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
                                        "date": datetime.date(1990, 10, 12),
                                        "price": 10000,
                                        "fruit": "raspberry",
                                        "amount": 1000000,
                                    })

        harvests = Harvest.objects.all()
        self.assertContains(response, "Earliest")
        self.assertContains(response, "4 digits")
        self.assertContains(response, "higher than 5000")
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
    # TODO implement
    pass
    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")

    def test_unauthorized_has_no_access(self):
        pass


class HarvestListViewTests(TestCase):
    pass

    def setUp(self):
        self.user = User.objects.create_user(username="testeruser", password="testeruserpass")

    def test_unauthorized_has_no_access(self):
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
