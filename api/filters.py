import django_filters

from api.models import Budget, Category


class CategoryFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )

    class Meta:
        model = Budget
        fields = ("category",)
