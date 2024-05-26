from django.contrib import admin
from .models import User,city,Restaurant,Customer,Table,Reservation,Menu,Street,Desert,Notification
# Register your models here.

admin.site.register(User)
admin.site.register(Restaurant)
admin.site.register(Customer)
admin.site.register(city)
admin.site.register(Table)
admin.site.register(Reservation)
admin.site.register(Menu)
admin.site.register(Street)
admin.site.register(Desert)
admin.site.register(Notification)

