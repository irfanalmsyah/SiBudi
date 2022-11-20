from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.registerview, name='register'),
    path('login/', views.loginview, name='login'),
    path('logout/', views.logoutview, name='logout'),
    path('transaction/', views.transaction, name='transaction'),
    path('transaction/<int:id>/', views.transaction_detail, name='transaction_detail'),
    path('category/', views.category, name='category'),
    path('wallet/', views.wallet, name='wallet'),
    path('shoppinglist/', views.shoppinglist, name='shoppinglist'),
    path('setting/', views.setting, name='setting'),
]