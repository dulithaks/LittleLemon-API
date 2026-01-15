from django.contrib import admin

# Register your models here.
from .models import Category, MenuItem, Cart, Order, OrderItem

admin.site.register(Category)