import random
import string
from unittest import TestCase

from django.contrib.auth.models import User
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from api.factories import (
    BudgetFactory,
    UserFactory,
    CategoryFactory,
    BudgetEntryFactory,
)
from api.models import Budget, BudgetEntry


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

    def test_create_budget_endpoint(self):
        category = CategoryFactory.create()
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

    def test_budget_entries_delete(self):
        self.client.force_authenticate(self.user)
        budget = BudgetFactory.create(user=self.user)
        budget_entry = BudgetEntryFactory.create(budget=budget)
        count = BudgetEntry.objects.count()
        r = self.client.delete(
            reverse("api:budget_entries-detail", kwargs={"pk": budget_entry.pk})
        )
        self.assertEqual(r.status_code, 204)
        self.assertEqual(BudgetEntry.objects.count(), count-1)
