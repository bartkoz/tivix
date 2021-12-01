from django.urls import path
from rest_framework.routers import SimpleRouter

from api import views

category_router = SimpleRouter()
category_router.register(
    r"category",
    views.CreateRetrieveListCategoryViewset,
    basename="category",
)

budget_router = SimpleRouter()
budget_router.register(
    r"budget",
    views.BudgetViewSet,
    basename="budget",
)

budget_entries_router = SimpleRouter()
budget_entries_router.register(
    r"budget_entries",
    views.BudgetEntryViewSet,
    basename="budget_entries",
)


urlpatterns = (
    [
        path("user/", views.CreateUserAPIView.as_view()),
    ]
    + category_router.urls
    + budget_router.urls
    + budget_entries_router.urls
)
