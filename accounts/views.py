from django.shortcuts import render
from .models import User
from.serializer import *
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Case, When, IntegerField


# Create your views here.

class AuthUserRegistrationView(APIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        if valid:
            serializer.validated_data['is_superuser'] = False
            serializer.validated_data['is_staff'] = False
            serializer.save()
            user=User.objects.get(username=request.data['username'])
            print(user)
            # Generate access token
            access_token = AccessToken.for_user(user)

            # Generate refresh token
            refresh_token = RefreshToken.for_user(user)

            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh_token),
                'user': serializer.data
            })
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)


class MobileAppLoginAPIView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = (AllowAny, )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        if valid:
            user=get_object_or_404(User,email=request.data['email'])
            status_code = status.HTTP_200_OK
             # Generate access token
            access_token = AccessToken.for_user(user)

            # Generate refresh token
            refresh_token = RefreshToken.for_user(user)

            return Response({
                'access_token': str(access_token),
                'refresh_token': str(refresh_token),
                'user': serializer.data
            })


class ReservationCreateView(generics.CreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        restaurant_id = request.data.get('restaurant')
        user_id = self.kwargs['user_id']  # Fetching user_id from URL parameter

        # Query the Customer model to get the customer_id associated with the user_id
        try:
            customer_id = Customer.objects.get(user_id=user_id).id
        except Customer.DoesNotExist:
            return Response({'error': 'Customer does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        tables = Table.objects.filter(restaurant_id=restaurant_id)
        menu_items = Menu.objects.filter(restaurant_id=restaurant_id)

        if not tables.exists() or not menu_items.exists():
            return Response({'error': 'No tables or menu items available for the given restaurant.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a mutable copy of request.data
        mutable_data = request.data.copy()
        # Add customer_id to the mutable copy
        mutable_data['customer'] = customer_id

        # Pass the modified data to serializer
        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def perform_create(self, serializer):
        # Save the reservation
        reservation = serializer.save()

         # Get the table associated with the reservation and mark it as reserved
        table = reservation.table
        table.is_reserved = True
        table.save()

        # Create a notification for the restaurant
        restaurant = reservation.restaurant
        notification = Notification.objects.create(
            created=timezone.now(),
            text=f"A new reservation has been made for {restaurant.name}.",
            User_id=restaurant.user,
        )

        # Optionally, you can add users (e.g., restaurant staff) to the notification
        # notification.users.set(users_list)
        # notification.save()

        return reservation
class TableViewSet(viewsets.ModelViewSet):
    serializer_class = TableSerializerCreateUpdateDelete

    def get_queryset(self):
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            return Table.objects.filter(restaurant_id=restaurant_id)
        return Table.objects.all()

class MenuViewSet(viewsets.ModelViewSet):
    serializer_class = MenuSerializerCreateUpdateDelete

    def get_queryset(self):
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            return Menu.objects.filter(restaurant_id=restaurant_id)
        return Menu.objects.all()

class TableListView(generics.ListAPIView):
    serializer_class = TableSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        return Table.objects.filter(restaurant_id=restaurant_id)

class MenuListView(generics.ListAPIView):
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        return Menu.objects.filter(restaurant_id=restaurant_id)

class DesertViewSet(viewsets.ModelViewSet):
    serializer_class = DesertSerializerCreateUpdateDelete

    def get_queryset(self):
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            return Desert.objects.filter(restaurant_id=restaurant_id)
        return Menu.objects.all()

class DesertListView(generics.ListAPIView):
    serializer_class = DesertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant_id = self.kwargs['restaurant_id']
        return Desert.objects.filter(restaurant_id=restaurant_id)

class ReservationstListView(generics.ListAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.kwargs['user_id']
        restaurant_id=Restaurant.objects.get(user=user)
        return Reservation.objects.filter(restaurant_id=restaurant_id)

@csrf_exempt
def list_restaurants(request,pk):
      # Extract token from request (assuming it's in the headers)
    token = request.headers.get('Authorization')
    if token:
        try:
            access_token = token.split()[1]
            # Decode the access token
            token = AccessToken(access_token)
            # Retrieve the user associated with the access token
            user = User.objects.get(id=pk)
            city = user.city.cityname
            street = user.street.StreetName if user.street else None
        except Exception as e:
            raise PermissionDenied(f"Invalid access token provided: {e}")
    else:
        raise PermissionDenied("Authorization header not provided")

    # Query restaurants based on the city and street
    if street:
        restaurants = Restaurant.objects.filter(city__cityname=city, street__StreetName=street)
    else:
        restaurants = Restaurant.objects.filter(city__cityname=city)

    # Serialize the queryset of restaurants
    # Annotate and order the restaurants based on whether both city and street match or only city matches
    restaurants = Restaurant.objects.annotate(
        match=Case(
            When(city__cityname=city, street__StreetName=street, then=2),
            When(city__cityname=city, then=1),
            default=0,
            output_field=IntegerField(),
        )
    ).order_by('-match', 'name')

    # Serialize the queryset of restaurants
    serializer = RestaurantSerializer(restaurants, many=True)

    # Return JSON response
    return JsonResponse(serializer.data, safe=False)



class ApproveReservationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reservation_id):
        try:
            reservation = Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found.'}, status=status.HTTP_404_NOT_FOUND)

        reservation.is_approved = True
        reservation.save()

        # Create a notification for the customer
        notification_text = f"Your reservation at {reservation.restaurant.name} has been approved."
        Notification.objects.create(
            created=timezone.now(),
            text=notification_text,
            User_id=reservation.customer.user,  # Notify the customer
        )

        return Response({'message': 'Reservation approved.'}, status=status.HTTP_200_OK)



#notication api


class UserNotificationsAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        return Notification.objects.filter(User_id=user)

class RestaurantByUserView(generics.RetrieveUpdateAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated,]

    def get_object(self):
        user_id = self.kwargs['user_id']
        return get_object_or_404(Restaurant, user_id=user_id)

class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializerCreateUpdateDelete
    permission_classes = (AllowAny, )

    def get_queryset(self):

        return city.objects.all()

class StreeViewSet(viewsets.ModelViewSet):
    serializer_class = StreetSerializerCreateUpdateDelete
    permission_classes = (AllowAny, )

    def get_queryset(self):

        return Street.objects.all()
@csrf_exempt
def RestaurantRetriveByUserView(request, user_id):
    try:
        restaurant = Restaurant.objects.get(user=user_id)
        restaurant_id = restaurant.pk
        return JsonResponse({'restaurant_id': restaurant_id})
    except Restaurant.DoesNotExist:
        return JsonResponse({'error': 'Restaurant not found for the given user ID'}, status=404)


