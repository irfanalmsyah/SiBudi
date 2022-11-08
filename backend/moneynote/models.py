from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    saldo = models.IntegerField(null=True, blank=True)


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    note = models.CharField(max_length=255, null=True, blank=True)
    nominal = models.IntegerField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.note


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.category_name
