from django.contrib.auth.models import User
from django.db import models


class TimestampAbstractModel(models.Model):
    created_at = models.DateTimeField(blank=True, auto_now_add=True)

    class Meta:
        abstract = True


class Category(TimestampAbstractModel):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Budget(TimestampAbstractModel):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, related_name="category_budgets", on_delete=models.PROTECT
    )
    user = models.ForeignKey(User, related_name="budgets", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class BudgetEntry(TimestampAbstractModel):
    class Types(models.TextChoices):
        EXPENSE = "EXP", "Expense"
        INCOME = "INC", "Income"

    name = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=3, choices=Types.choices)
    budget = models.ForeignKey(Budget, related_name="entries", on_delete=models.CASCADE)

    def __str__(self):
        return self.name
