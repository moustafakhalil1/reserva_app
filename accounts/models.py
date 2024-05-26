import uuid

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
from django.db.models.signals import post_save
from .management import CustomUserManager

class city(models.Model):
      cityname=models.CharField(unique=True,max_length=40)
      def __str__(self):
            return self.cityname
class Street(models.Model):
      StreetName=models.CharField(unique=True,max_length=40)
      def __str__(self):
            return self.StreetName
class cityn(models.Model):
      cityname=models.CharField(unique=True,max_length=40)
      def __str__(self):
            return self.cityname      

class User(AbstractBaseUser, PermissionsMixin):
  
  # These fields tie to the roles!
    Customer = 1
    RESTAURANT = 2
  

    ROLE_CHOICES = (
        (Customer, 'Customer'),
        (RESTAURANT, 'RESTAURANT'),
     
    )

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
    # Roles created here
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, verbose_name='Public identifier')
    username=models.CharField(max_length=40,unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=30, blank=True)
    city=models.ForeignKey(city,on_delete=models.SET_NULL,null=True)
    street = models.ForeignKey(Street,on_delete=models.SET_NULL,null=True,blank=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)
    created_by = models.EmailField()
    modified_by = models.EmailField()
   


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()
    def save(self, *args, **kwargs):
        if self.role is None:
            self.role = self.CUSTOMER  # Set default role if none provided
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
class Profile(models.Model):
     user=models.OneToOneField(User,on_delete=models.CASCADE)
     image=models.ImageField(default="defualt.jpg",upload_to='user_image')
     verfied=models.BooleanField(default=False)
     def __str__(self) -> str:
           return 'self.user'


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Restaurant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=True,blank=True)
    image=models.ImageField(upload_to='images/',blank=True)
    city = models.ForeignKey(city,on_delete=models.SET_NULL,null=True)
    street = models.ForeignKey(Street,on_delete=models.SET_NULL,null=True,blank=True)
    phone_number = models.CharField(max_length=15, null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    def __str__(self):
        return str(self.user)

class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    table_number = models.CharField(max_length=10)
    capacity = models.PositiveIntegerField()
    is_reserved=models.BooleanField(default=False,null=True,blank=True)
    def __str__(self):
        return f"Table {self.table_number} at {self.restaurant}"

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} at {self.restaurant}"
class Desert(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"{self.name} at {self.restaurant}"

class Reservation(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    menu_items = models.ManyToManyField(Menu)
    Desert_items = models.ManyToManyField(Desert,blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    reservation_time = models.DateTimeField()
    is_approved=models.BooleanField(default=False,null=True,blank=True)
    
    def __str__(self):
        return f"Order Reseved {self.id} by {self.customer.user.email} at {self.restaurant.name}"
class Notification(models.Model):
    created = models.DateTimeField()
    text = models.TextField()
    User_id = models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True)
    def __str__(self):
        return f"notify {self.User_id}"

def create_profile_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

def save_profile_user(sender, instance, **kwargs):
    instance.profile.save()

def create_customer_or_restaurant(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.Customer:
            Customer.objects.create(user=instance)
        elif instance.role == User.RESTAURANT:
            Restaurant.objects.create(user=instance)

post_save.connect(create_profile_user, sender=User)
post_save.connect(save_profile_user, sender=User)
post_save.connect(create_customer_or_restaurant, sender=User)    