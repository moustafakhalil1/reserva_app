from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    class Meta:
        model=User
        fields=['id','email','full_name','username','password','password_confirm','city','street','role']
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError("Passwords do not match")
        return attrs
    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user



class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    role = serializers.CharField(read_only=True)
    id = serializers.IntegerField(read_only=True)  # Add this field for user ID

    def update(self, instance, validated_data):
        pass

    def validate(self, data):
        email = data['email']
        password = data['password']
        user = authenticate(email=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid login credentials")

        try:
            validation = {
                'id':user.id,
                'email': user.email,
                'password':user.password,
                'role': user.role,
                'street': user.street,
                'city': user.city,
            }

            return validation
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid login credentials")


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id','is_reserved','table_number', 'capacity']
class TableSerializerCreateUpdateDelete(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id','is_reserved','table_number', 'capacity','restaurant']

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id', 'name', 'description', 'price']
class MenuSerializerCreateUpdateDelete(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['id','restaurant', 'name', 'description', 'price']

class DesertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Desert
        fields = ['id', 'name', 'description', 'price']
class DesertSerializerCreateUpdateDelete(serializers.ModelSerializer):
    class Meta:
        model = Desert
        fields = ['id','restaurant', 'name', 'description', 'price']
class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id','customer', 'restaurant', 'menu_items','Desert_items','table', 'reservation_time', 'total_price']


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id','user', 'name', 'image','description','city', 'street', 'phone_number']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'created', 'text', 'User_id']

class CitySerializerCreateUpdateDelete(serializers.ModelSerializer):
    class Meta:
        model = city
        fields = ['id','cityname']
class StreetSerializerCreateUpdateDelete(serializers.ModelSerializer):
    class Meta:
        model = Street
        fields = ['id','StreetName']

