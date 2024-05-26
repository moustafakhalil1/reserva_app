from django.urls import path,include
from .views import *
from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'tables', TableViewSet, basename='table')
router.register(r'menus', MenuViewSet, basename='menu')
router.register(r'Desert', DesertViewSet, basename='Desert')

urlpatterns=[
    path('', include(router.urls)),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/access', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/',AuthUserRegistrationView.as_view(),name='users'),
    path('login/',MobileAppLoginAPIView.as_view(),name='login'),
    path('restaurantsList/<int:pk>/',list_restaurants,name='list-restaurants'),
    path('reservations/create/', ReservationCreateView.as_view(), name='reservation-create'),
    path('restaurants/<int:restaurant_id>/tables/', TableListView.as_view(), name='table-list'),
    path('restaurants/<int:restaurant_id>/menu/', MenuListView.as_view(), name='menu-list'),
    path('restaurants/<int:restaurant_id>/Desert/', DesertListView.as_view(), name='Desert-list'),
    # path('users', UserListView.as_view(), name='users'),
    path('restaurants/<int:user_id>/Reservations/', ReservationstListView.as_view(), name='Reservataion-list'),
    path('reservations/<int:reservation_id>/approve/', ApproveReservationAPIView.as_view(), name='approve-reservation'),
   
    path('notifications/<int:user_id>/', UserNotificationsAPIView.as_view(), name='user-notifications'),


]