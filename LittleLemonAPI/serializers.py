from datetime import date

from django.contrib.auth.models import Group, User
from rest_framework import serializers

from utils.get_group import get_group
from .models import Cart, MenuItem, Order
from .validators import unique_menuitem_title


class MenuItemsCartSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)


class MenuItemSerializer(serializers.ModelSerializer):
    title = serializers.CharField(validators=[unique_menuitem_title])

    class Meta:
        model = MenuItem
        fields = [
            'id',
            'title',
            'price',
            'featured',
            'category'
        ]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        ]

    def create(self, validated_data):
        path = self.context['request'].get_full_path()
        group_name = get_group(path)
        group = Group.objects.get(name=group_name)
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.groups.add(group.id)
        user.save()
        return user


class CartSerializer(serializers.ModelSerializer):
    menuitem_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    menuitem = MenuItemsCartSerializer(read_only=True)
    unit_price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = [
            'user_id',
            'menuitem_id',
            'menuitem',
            'quantity',
            'unit_price',
            'price'
        ]


class OrderSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    user_id = serializers.CharField(source='user.id', read_only=True)
    total = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    date = serializers.DateField(default=date.today())
    order_items = serializers.ReadOnlyField(source='get_order_items')

    class Meta:
        model = Order
        fields = [
            'id',
            'user_id',
            'delivery_crew',
            'status',
            'total',
            'date',
            'order_items'
        ]


class OrderItemsSerializer(serializers.ModelSerializer):
    order_items = serializers.ReadOnlyField(source='get_order_items')

    class Meta:
        model = Order
        fields = [
            'order_items'
        ]
