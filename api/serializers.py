from rest_framework import serializers

from api.models import Category, Budget, BudgetEntry


class CreateUserSerializer(serializers.Serializer):

    password1 = serializers.CharField(min_length=10, max_length=255)
    password2 = serializers.CharField(min_length=10, max_length=255)
    username = serializers.CharField(max_length=255)

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError("Password does not match!")
        return attrs


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("name", "id")


class BudgetEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetEntry
        fields = ("name", "type", "value", "id", "budget")


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ("category", "name")


class BudgetDetailSerializer(serializers.ModelSerializer):

    entries = BudgetEntrySerializer(many=True, required=False)
    category = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = ("category", "entries", "name", "id")

    def get_category(self, obj):
        return obj.category.name
