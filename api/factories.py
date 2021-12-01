import factory
from django.contrib.auth.models import User
from factory.fuzzy import FuzzyInteger, FuzzyChoice, FuzzyText

from api.models import BudgetEntry, Budget, Category


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = FuzzyText(length=12)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker("sentence", nb_words=2)


class BudgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Budget

    name = factory.Faker("sentence", nb_words=2)
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)


class BudgetEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BudgetEntry

    name = factory.Faker("sentence", nb_words=2)
    value = FuzzyInteger(1, 1000)
    type = FuzzyChoice(BudgetEntry.Types)
    budget = factory.SubFactory(BudgetFactory)
