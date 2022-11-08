from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.loginview, name='login'),
    path('logout/', views.logoutview, name='logout'),
    path('transaction/', views.addtransaction, name='addtransaction'),
    path('transaction/<int:id>/', views.transactiondetails, name='transaction'),
    path('category/', views.category, name='category'),
    path('register/', views.registerview, name='register'),
    path('saldo/', views.saldo, name='saldo'),
]
