from django.db import models


class TimestampAbstractModel(models.Model):
    created_at = models.DateTimeField(blank=True, auto_now_add=True)

    class Meta:
        abstract = True


class Category(TimestampAbstractModel):
    name = models.CharField(max_length=255)


class Budget(TimestampAbstractModel):
    category = models.ForeignKey(Category, related_name='budgets', on_delete=models.PROTECT)


class BudgetEntry(TimestampAbstractModel):

    class Types(models.TextChoices):
        EXPENSE = 'EXP', 'Expense'
        INCOME = 'INC', 'Income'

    value = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=3, choices=Types.choices)
    budget = models.ForeignKey(Budget, related_name='entries', on_delete=models.CASCADE)
