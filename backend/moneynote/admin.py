from django.contrib import admin
from .models import Transaction, Category, Wallet

admin.site.register(Transaction)
admin.site.register(Category)
admin.site.register(Wallet)
