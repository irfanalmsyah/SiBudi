from django.shortcuts import render, redirect
from .models import Transaction, Category, User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

@login_required
def index(request):
    incomes = Transaction.objects.filter(user=request.user, nominal__gt=0)
    expenses = Transaction.objects.filter(user=request.user, nominal__lt=0)
    categories = Category.objects.filter(user=request.user)
    context = {
        'incomes': incomes,
        'expenses': expenses,
        'saldo': request.user.saldo,
        'categories': categories,
    }
    return render(request, 'index.html', context=context)


def registerview(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login/')
        else:
            message = ''
            formerr = form.errors.as_data()
            for i in formerr:
                for j in formerr[i]:
                    message += j.messages[0] + ' '
            context = {'message': message}
            return render(request, 'register.html', context)
    return render(request, 'register.html')


def loginview(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            context = {'message': 'Username atau password salah'}
            return render(request, 'login.html', context)
    return render(request, 'login.html')


def logoutview(request):
    logout(request)
    return redirect('index')


@login_required
def saldo(request):
    if request.method == 'POST':
        saldo = request.POST['saldo']
        request.user.saldo = saldo
        request.user.save()
    return redirect('index')


@login_required
def addtransaction(request):
    if request.method == 'POST':
        category_id = request.POST['category']
        note = request.POST['note']
        if request.POST['type'] == 'income':
            nominal = int(request.POST['nominal'])
        else:
            nominal = int(request.POST['nominal']) * -1

        if request.user.saldo is not None:
            request.user.saldo += nominal

        try:
            category = Category.objects.get(user=request.user, category_id=category_id)
            transaction = Transaction(user=request.user, category=category, nominal=nominal, note=note)
        except:
            transaction = Transaction(user=request.user, nominal=nominal, note=note)

        transaction.save()
        request.user.save()
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def transactiondetails(request, id):
    try:
        transaction = Transaction.objects.get(id=id, user=request.user)
    except:
        raise PermissionDenied

    if request.method == 'POST':
        if request.POST['method'] == 'update':
            if int(request.POST['nominal']) < 0:
                return redirect(request.META.get('HTTP_REFERER'))
            transaction.note = request.POST['note']
            request.user.saldo -= transaction.nominal
            if request.POST['type'] == 'income':
                transaction.nominal = int(request.POST['nominal'])
            else:
                transaction.nominal = int(request.POST['nominal']) * -1
            request.user.saldo += transaction.nominal
            request.user.save()

            category_id = request.POST['category']
            try:
                category = Category.objects.get(user=request.user, category_id=category_id)
                transaction.category = category
            except:
                transaction.category = None
            transaction.save()
        elif request.POST['method'] == 'delete':
            request.user.saldo -= transaction.nominal
            transaction.delete()
            request.user.save()
            return redirect('index')
    else:
        categories = Category.objects.filter(user=request.user)
        if transaction.nominal < 0:
            isExpense = True
        else:
            isExpense = False
        context = {
            'id': transaction.id,
            'note': transaction.note,
            'date': transaction.date,
            'nominal': transaction.nominal,
            'category': transaction.category,
            'categories': categories,
            'isExpense': isExpense,
        }
        return render(request, 'transaction.html', context=context)
    
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def category(request):
    if request.method == 'POST':
        if request.POST['method'] == 'create':
            category = Category()
            category.user_id = request.user.id
            category.category_name = request.POST['category_name']
            category.save()
        elif request.POST['method'] == 'delete':
            category = Category.objects.get(category_id=request.POST['category_id'], user_id=request.user.id)
            transaction = Transaction.objects.filter(category=category)
            for i in transaction:
                i.category = None
                i.save()
            category.delete()
        elif request.POST['method'] == 'update':
            category = Category.objects.get(category_id=request.POST['category_id'], user_id=request.user.id)
            category.category_name = request.POST['category_name']
            category.save()

    return redirect(request.META.get('HTTP_REFERER'))
