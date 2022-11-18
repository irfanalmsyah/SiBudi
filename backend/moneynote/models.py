from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    note = models.CharField(max_length=255, null=True, blank=True)
    nominal = models.IntegerField()
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    wallet = models.ForeignKey('Wallet', on_delete=models.PROTECT , null=False, blank=False)

    def __str__(self):
        return self.note


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.category_name


class Wallet(models.Model):
    wallet_id = models.AutoField(primary_key=True)
    wallet_name = models.CharField(max_length=100, null=False, blank=False)
    wallet_saldo = models.IntegerField(null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.wallet_name
