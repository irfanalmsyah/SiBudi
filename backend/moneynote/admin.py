from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin
from .models import Transaction, Category

admin.site.register(User, UserAdmin)
admin.site.register(Transaction)
admin.site.register(Category)
