import random
import string
from unittest import TestCase

from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from api.factories import (
    BudgetFactory,
    UserFactory,
    CategoryFactory,
    BudgetEntryFactory,
)
from api.filters import CategoryFilter
from api.models import Budget, BudgetEntry
from api.serializers import CreateUserSerializer, CategorySerializer, BudgetSerializer


class APITests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = APIClient()
        cls.user = UserFactory.create()

    def tearDown(self):
        self.client.logout()

    def test_user_create_endpoint(self):
        count = User.objects.count()
        data = {
            "password1": "pass123456789",
            "password2": "pass123456789",
            "username": "".join(random.choice(string.ascii_letters) for i in range(15)),
        }
        r = self.client.post(reverse("api:create_user"), data=data)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(User.objects.count(), count + 1)

    def test_budget_list_no_login_endpoint(self):
        r = self.client.get(reverse("api:budget-list"))
        self.assertEqual(r.status_code, 403)

    def test_budget_list_endpoint(self):
        user = UserFactory.create()
        self.client.force_authenticate(user=user)
        r = self.client.get(reverse("api:budget-list"))
        self.assertEqual(r.status_code, 200)

    def test_budget_list_only_list_budgets_belonging_to_user(self):
        user2 = UserFactory.create()
        BudgetFactory(user=self.user)
        # create few more budgets that belong to someone else
        for i in range(3):
            BudgetFactory(user=user2)
        self.client.force_authenticate(user=self.user)
        r = self.client.get(reverse("api:budget-list"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["results"]), self.user.budgets.count())

    def test_budget_detail_endpoint(self):
        budget = BudgetFactory.create()
        r = self.client.get(reverse("api:budget-detail", kwargs={"pk": budget.pk}))
        self.assertEqual(r.status_code, 200)

    def test_update_budget_endpoint(self):
        budget = BudgetFactory.create(user=self.user)
        self.client.force_authenticate(user=self.user)
        data = {"name": "diffname"}
        r = self.client.patch(
            reverse("api:budget-detail", kwargs={"pk": budget.pk}), data=data
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Budget.objects.get(pk=budget.pk).name, "diffname")

    def test_update_budget_endpoint(self):
        budget = BudgetFactory.create()
        self.client.force_authenticate(user=self.user)
        data = {"name": "diffname"}
        r = self.client.patch(
            reverse("api:budget-detail", kwargs={"pk": budget.pk}), data=data
        )
        self.assertEqual(r.status_code, 404)
        self.assertEqual(Budget.objects.get(pk=budget.pk).name, budget.name)

    def test_create_budget_endpoint(self):
        category = CategoryFactory.create(user=self.user)
        data = {"category": category.pk, "name": "test"}
        count = Budget.objects.count()
        self.client.force_authenticate(self.user)
        r = self.client.post(reverse("api:budget-list"), data=data)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(Budget.objects.count(), count + 1)

    def test_delete_budget_endpoint(self):
        self.client.force_authenticate(self.user)
        budget = BudgetFactory.create(user=self.user)
        count = Budget.objects.count()
        r = self.client.delete(reverse("api:budget-detail", kwargs={"pk": budget.pk}))
        self.assertEqual(r.status_code, 204)
        self.assertEqual(Budget.objects.count(), count - 1)

    def test_delete_budget_endpoint_unowned(self):
        self.client.force_authenticate(self.user)
        budget = BudgetFactory.create()
        count = Budget.objects.count()
        r = self.client.delete(reverse("api:budget-detail", kwargs={"pk": budget.pk}))
        self.assertEqual(r.status_code, 404)
        self.assertEqual(Budget.objects.count(), count)

    def test_budget_entries_create(self):
        self.client.force_authenticate(self.user)
        budget = BudgetFactory.create(user=self.user)
        data = {"name": "asdasda", "type": "EXP", "value": 1234, "budget": budget.pk}
        count = BudgetEntry.objects.count()
        r = self.client.post(reverse("api:budget_entries-list"), data=data)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(BudgetEntry.objects.count(), count + 1)

    def test_budget_entries_update(self):
        self.client.force_authenticate(self.user)
        budget = BudgetFactory.create(user=self.user)
        budget_entry = BudgetEntryFactory.create(budget=budget)
        data = {
            "name": "diffname",
        }
        r = self.client.patch(
            reverse("api:budget_entries-detail", kwargs={"pk": budget_entry.pk}),
            data=data,
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(BudgetEntry.objects.get(pk=budget_entry.pk).name, "diffname")

    def test_budget_entries_update_unowned(self):
        self.client.force_authenticate(self.user)
        budget = BudgetFactory.create()
        budget_entry = BudgetEntryFactory.create(budget=budget)
        data = {
            "name": "diffname",
        }
        r = self.client.patch(
            reverse("api:budget_entries-detail", kwargs={"pk": budget_entry.pk}),
            data=data,
        )
        self.assertEqual(r.status_code, 404)
        self.assertEqual(
            BudgetEntry.objects.get(pk=budget_entry.pk).name, budget_entry.name
        )

    def test_budget_entries_delete(self):
        self.client.force_authenticate(self.user)
        budget = BudgetFactory.create(user=self.user)
        budget_entry = BudgetEntryFactory.create(budget=budget)
        count = BudgetEntry.objects.count()
        r = self.client.delete(
            reverse("api:budget_entries-detail", kwargs={"pk": budget_entry.pk})
        )
        self.assertEqual(r.status_code, 204)
        self.assertEqual(BudgetEntry.objects.count(), count - 1)

    def test_budget_entries_delete_unowned(self):
        self.client.force_authenticate(self.user)
        budget = BudgetFactory.create()
        budget_entry = BudgetEntryFactory.create(budget=budget)
        count = BudgetEntry.objects.count()
        r = self.client.delete(
            reverse("api:budget_entries-detail", kwargs={"pk": budget_entry.pk})
        )
        self.assertEqual(r.status_code, 404)
        self.assertEqual(BudgetEntry.objects.count(), count)


class FilterTests(TestCase):
    def test_category_filter(self):
        budget = BudgetFactory.create()
        checkup = budget.category.name
        expected_count = Budget.objects.filter(
            category__name__icontains=checkup
        ).count()
        filter_obj = CategoryFilter(
            data={"category": checkup}, queryset=Budget.objects.all()
        )
        self.assertEqual(filter_obj.qs.count(), expected_count)


class SerializerTests(TestCase):
    def test_user_serializer_different_passwords(self):
        data = {
            "password1": "password123456789",
            "password2": "password987654321",
            "username": "".join(random.choice(string.ascii_letters) for i in range(15)),
        }
        serializer = CreateUserSerializer(data=data)
        self.assertRaises(ValidationError, serializer.is_valid, raise_exception=True)

    def test_user_serializer_same_passwords(self):
        data = {
            "password1": "password123456789",
            "password2": "password123456789",
            "username": "".join(random.choice(string.ascii_letters) for i in range(15)),
        }
        serializer = CreateUserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_category_serializer(self):
        cat = CategoryFactory.create()
        serializer = CategorySerializer(cat)
        self.assertEqual(serializer.data, {"name": cat.name, "id": cat.pk})

    def test_budget_entry_serializer(self):
        be = BudgetEntryFactory.create()
        serializer = CategorySerializer(be)
        self.assertEqual(serializer.data, {"name": be.name, "id": be.pk})

    def test_budget_serializer(self):
        budget = BudgetFactory.create()
        serializer = BudgetSerializer(budget)
        self.assertEqual(
            serializer.data, {"category": budget.category_id, "name": budget.name}
        )
