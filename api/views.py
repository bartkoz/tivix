from django.contrib.auth.models import User
from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import CategoryFilter
from api.models import Category, Budget, BudgetEntry
from api.paginators import CustomPaginator
from api.serializers import (
    CreateUserSerializer,
    CategorySerializer,
    BudgetSerializer,
    BudgetEntrySerializer,
    BudgetDetailSerializer,
)


class CustomCreateMixin:

    model_class = None

    def create(self, request, *args, **kwargs):
        if not self.model_class:
            raise NotImplementedError("Model class has to be specified.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.model_class.objects.create(
            user_id=request.user.pk, **serializer.validated_data
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class CreateUserAPIView(APIView):

    queryset = User.objects.all()
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_credentials = {
            "password": serializer["password1"],
            "username": serializer["username"],
        }
        try:
            User.objects.create(**user_credentials)
        except IntegrityError:
            # most probably it's already existing username but u don't want to spoil such info
            return Response("Something went wrong.", status=status.HTTP_400_BAD_REQUEST)
        return Response({"User created"}, status=status.HTTP_201_CREATED)


class CategoryViewset(
    CustomCreateMixin,
    viewsets.ModelViewSet,
):

    serializer_class = CategorySerializer
    pagination_class = CustomPaginator
    model_class = Category

    def get_queryset(self):
        return Category.objects.filter(user_id=self.request.user.pk).order_by("name")


class BudgetViewSet(CustomCreateMixin, viewsets.ModelViewSet):

    model_class = Budget
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPaginator
    filterset_class = CategoryFilter
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ["update", "partial_update", "create"]:
            return BudgetSerializer
        return BudgetDetailSerializer

    def get_queryset(self):
        if self.action == "retrieve":
            return Budget.objects.all()
        return Budget.objects.filter(user_id=self.request.user.pk).order_by("name")

    def get_permissions(self):
        if self.action == "retrieve":
            return []
        return super().get_permissions()


class BudgetEntryViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    model_class = BudgetEntry
    serializer_class = BudgetEntrySerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPaginator

    def get_queryset(self):
        return BudgetEntry.objects.filter(
            budget__in=self.request.user.budgets.all()
        ).order_by("name")
