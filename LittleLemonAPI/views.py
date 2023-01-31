from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import (DestroyAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.filters import SearchFilter

from utils.get_group import get_group
from .exceptions import BadRequestException, ConflictException, PreconditionFailedException
from .models import Cart, MenuItem, Order, OrderItem
from .pagination import MenuItemsPagination, OrderPagination
from .permissions import IsManagerPermission
from .serializers import CartSerializer, MenuItemSerializer, OrderItemsSerializer, OrderSerializer, UserSerializer


class MenuItemsListCreateApiView(ListCreateAPIView):
    queryset = MenuItem.objects.all()
    pagination_class = MenuItemsPagination
    serializer_class = MenuItemSerializer
    permission_classes = [DjangoModelPermissions]

    filterset_fields = ('featured', 'category')
    ordering_fields = ['price']
    search_fields = ['title']


class MenuItemsRetrieveUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [DjangoModelPermissions]
    lookup_field = 'pk'


class ManagersListCreateApiView(ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [DjangoModelPermissions, IsManagerPermission]

    def get_queryset(self):
        path = self.request.get_full_path()
        group = get_group(path)
        return User.objects.all().filter(groups__name=group)


class ManagersDestroyApiView(DestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [DjangoModelPermissions]
    lookup_field = 'pk'

    def get_queryset(self):
        path = self.request.get_full_path()
        group = get_group(path)
        return User.objects.all().filter(groups__name=group)


class CartListCreateApiView(ListCreateAPIView):
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.all().filter(user=user)

    def perform_create(self, serializer):
        data = serializer.validated_data
        try:
            menu_items = MenuItem.objects.all()
            unit_price = menu_items.get(id=data['menuitem_id']).price
            price = unit_price * data['quantity']

            serializer.save(
                user=self.request.user,
                unit_price=unit_price,
                price=price)
        except IntegrityError:
            raise ConflictException('Item already exists')
        except Exception as e:
            raise Exception(f'Unhandled error {e}')

    def delete(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderItemsListCreateApiView(ListCreateAPIView):
    serializer_class = OrderSerializer
    pagination_class = OrderPagination

    filterset_fields = ('delivery_crew', 'status', 'user')
    ordering_fields = ['total', 'date']

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='manager').exists():
            return Order.objects.all()

        elif user.groups.filter(name='delivery-crew').exists():
            return Order.objects.all().filter(delivery_crew=user.id)

        return Order.objects.all().filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        cart = Cart.objects.all().filter(user=user)

        if len(cart.values()) != 0:
            total = 0
            for cart_item in cart.values():
                total += cart_item.get('price')

            order = serializer.save(
                user=user,
                total=total
            )

            for cart_item in cart.values():
                menu_item = MenuItem.objects.get(id=cart_item.get('menuitem_id'))
                OrderItem.objects.create(
                    order=order,
                    menuitem=menu_item,
                    quantity=cart_item.get('quantity'),
                    unit_price=cart_item.get('unit_price'),
                    price=cart_item.get('price')
                )

            cart.delete()

        else:
            raise PreconditionFailedException('Cart is empty')


class OrderRetrieveUpdateDestroyApiView(RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='manager').exists():
            return Order.objects.all()

        elif user.groups.filter(name='delivery-crew').exists():
            return Order.objects.all().filter(delivery_crew=user.id)

        return Order.objects.all().filter(user=user)

    def get(self, request, *args, **kwargs):
        self.serializer_class = OrderItemsSerializer
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        body = request.POST
        is_manager = request.user.groups.filter(name='manager').exists()
        is_delivery_crew = request.user.groups.filter(name='delivery-crew').exists()

        if is_manager or is_delivery_crew:

            if body.get('status') or body.get('delivery_crew'):
                if is_manager:
                    user = User.objects.get(id=body.get('delivery_crew'))
                    if user.groups.filter(name='delivery-crew').exists():
                        return self.partial_update(request, *args, **kwargs)
                    else:
                        raise NotFound("Delivery crew member not found")

                if is_delivery_crew and body.get('delivery_crew'):
                    raise PermissionDenied()

                if is_delivery_crew and body.get('status'):
                    return self.partial_update(request, *args, **kwargs)

            else:
                raise BadRequestException()

        else:
            raise PermissionDenied()

    def delete(self, request, *args, **kwargs):
        if request.user.groups.filter(name='manager').exists():
            return self.destroy(request, *args, **kwargs)
        else:
            raise PermissionDenied()
