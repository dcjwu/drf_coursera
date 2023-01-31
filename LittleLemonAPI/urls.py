from django.urls import path

from .views import (CartListCreateApiView, ManagersDestroyApiView, ManagersListCreateApiView,
                    MenuItemsListCreateApiView, MenuItemsRetrieveUpdateDestroyApiView, OrderItemsListCreateApiView, OrderRetrieveUpdateDestroyApiView)

urlpatterns = [
    path('menu-items/', MenuItemsListCreateApiView.as_view()),
    path('menu-items/<int:pk>/', MenuItemsRetrieveUpdateDestroyApiView.as_view()),

    path('groups/manager/users/', ManagersListCreateApiView.as_view()),
    path('groups/manager/users/<int:pk>/', ManagersDestroyApiView.as_view()),
    path('groups/delivery-crew/users/', ManagersListCreateApiView.as_view()),
    path('groups/delivery-crew/users/<int:pk>/', ManagersDestroyApiView.as_view()),

    path('cart/menu-items/', CartListCreateApiView.as_view()),

    path('orders/', OrderItemsListCreateApiView.as_view()),
    path('orders/<int:pk>/', OrderRetrieveUpdateDestroyApiView.as_view()),

]
