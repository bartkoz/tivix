from django.contrib.auth.models import User
from rest_framework import mixins, generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.models import Category, Budget, BudgetEntry
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


class CreateUserAPIView(generics.CreateAPIView):

    queryset = User.objects.all()
    serializer_class = CreateUserSerializer


class CreateRetrieveListCategoryViewset(
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BudgetViewSet(CustomCreateMixin, viewsets.ModelViewSet):

    model_class = Budget
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ["update", "partial_update", "create"]:
            return BudgetSerializer
        return BudgetDetailSerializer

    def get_queryset(self):
        if self.action == "retrieve":
            return Budget.objects.all()
        return Budget.objects.filter(user_id=self.request.user.pk)

    def get_permissions(self):
        if self.action == "retrieve":
            return []
        return super().get_permissions()


class BudgetEntryViewSet(
    CustomCreateMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):

    model_class = BudgetEntry
    serializer_class = BudgetEntrySerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return BudgetEntry.objects.filter(user_id=self.request.user.pk)
