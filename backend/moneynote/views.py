from django.shortcuts import render, redirect
from .models import Transaction, Category, Wallet, ShoppingList
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import PermissionDenied
from django.db.models import Sum


@login_required
def index(request):
    context = {
        'incomes': Transaction.objects.filter(user=request.user, transaction_nominal__gt=0).order_by('-transaction_date'),
        'expenses': Transaction.objects.filter(user=request.user, transaction_nominal__lt=0).order_by('-transaction_date'),
        'categories': Category.objects.filter(user=request.user),
        'wallets': Wallet.objects.filter(user=request.user),
        'saldo': Wallet.objects.filter(user=request.user).aggregate(total=Sum('wallet_saldo'))['total']
    }
    return render(request, 'index.html', context=context)


def registerview(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password1']) 
            login(request, user)
            wallet = Wallet()
            wallet.user_id = user.id
            wallet.wallet_name = 'Cash'
            wallet.wallet_saldo = 0
            wallet.save()
            return redirect('index')
        else:
            message = ''
            formerr = form.errors.as_data()
            for i in formerr:
                for j in formerr[i]:
                    message += j.messages[0] + ' '
            context = {'message': message}
            return render(request, 'register.html', context)
    return render(request, 'register.html')


@login_required
def setting(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('setting')
        else:
            message = ''
            formerr = form.errors.as_data()
            for i in formerr:
                for j in formerr[i]:
                    message += j.messages[0] + ' '
            context = {'message': message}
            return render(request, 'setting.html', context)
    else:
        return render(request, 'setting.html')


def loginview(request):
    if request.user.is_authenticated:
        return redirect('/')
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
def transaction(request):
    if request.method == 'POST':
        note = request.POST['note']
        category = request.POST['category']
        wallet = request.POST['wallet']
        date = request.POST['date']
        if request.POST['type'] == 'income':
            nominal = int(request.POST['nominal'])
        else:
            nominal = int(request.POST['nominal']) * -1
        Transaction.objects.create(
            user=request.user,
            transaction_note=note,
            transaction_nominal=nominal,
            transaction_date=date,
            category_id=category,
            wallet_id=wallet,
        )
        wallet = Wallet.objects.get(wallet_id=wallet)
        wallet.wallet_saldo += nominal
        wallet.save()
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        context = {
            'incomes': Transaction.objects.filter(user=request.user, transaction_nominal__gt=0).order_by('-transaction_date'),
            'expenses': Transaction.objects.filter(user=request.user, transaction_nominal__lt=0).order_by('-transaction_date'),
            'categories': Category.objects.filter(user=request.user),
            'wallets': Wallet.objects.filter(user=request.user),
        }
        return render(request, 'transaction.html', context=context)


@login_required
def transactiondetails(request, id):
    try:
        transaction = Transaction.objects.get(transaction_id=id, user=request.user)
    except:
        raise PermissionDenied

    if request.method == 'POST':
        if request.POST['method'] == 'update':
            wallet_id = request.POST['wallet']
            wallet = Wallet.objects.get(wallet_id=wallet_id)
            wallet.wallet_saldo -= transaction.transaction_nominal
            transaction.transaction_note = request.POST['note']
            transaction.transaction_date = request.POST['date']
            if request.POST['type'] == 'income':
                nominal = int(request.POST['nominal'])
            else:
                nominal = int(request.POST['nominal']) * -1
            transaction.transaction_nominal = nominal
            wallet.wallet_saldo += transaction.transaction_nominal
            wallet.save()
            category_id = request.POST['category']
            try:
                category = Category.objects.get(user=request.user, category_id=category_id)
                transaction.category = category
            except:
                transaction.category = None
            try:
                wallet = Wallet.objects.get(user=request.user, wallet_id=wallet_id)
                transaction.wallet = wallet
            except:
                transaction.wallet = None
            transaction.save()
            return redirect(request.META.get('HTTP_REFERER'))
        elif request.POST['method'] == 'delete':
            wallet = Wallet.objects.get(wallet_id=transaction.wallet_id)
            wallet.wallet_saldo -= transaction.transaction_nominal
            wallet.save()
            transaction.delete()
            return redirect('transaction')
    else:
        categories = Category.objects.filter(user=request.user)
        wallets = Wallet.objects.filter(user=request.user)
        if transaction.transaction_nominal < 0:
            isExpense = True
        else:
            isExpense = False
        context = {
            'id': transaction.transaction_id,
            'note': transaction.transaction_note,
            'date': transaction.transaction_date,
            'nominal': transaction.transaction_nominal,
            'trcategory': transaction.category,
            'trwallet': transaction.wallet,
            'categories': categories,
            'wallets': wallets,
            'isExpense': isExpense,
        }
        return render(request, 'transactiondetails.html', context=context)


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
    else:
        context = {
            'categories': Category.objects.filter(user=request.user),
        }
        return render(request, 'category.html', context=context)


@login_required
def wallet(request):
    if request.method == 'POST':
        if request.POST['method'] == 'create':
            wallet = Wallet()
            wallet.user_id = request.user.id
            wallet.wallet_name = request.POST['wallet_name']
            wallet.wallet_saldo = int(request.POST['wallet_saldo']) 
            wallet.save()
        elif request.POST['method'] == 'delete':
            wallet = Wallet.objects.get(wallet_id=request.POST['wallet_id'], user_id=request.user.id)
            cash = Wallet.objects.filter(user=request.user, wallet_name='Cash').first()
            Transaction.objects.filter(wallet=wallet).update(wallet=cash)
            cash.wallet_saldo += wallet.wallet_saldo
            cash.save()
            wallet.delete()
        elif request.POST['method'] == 'update':
            wallet = Wallet.objects.get(wallet_id=request.POST['wallet_id'], user_id=request.user.id)
            wallet.wallet_name = request.POST['wallet_name']
            wallet.wallet_saldo = request.POST['wallet_saldo']
            wallet.save()
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        cash = Wallet.objects.filter(user=request.user, wallet_name='Cash').first()
        context = {
            'cash': cash,
            'wallets': Wallet.objects.filter(user=request.user).exclude(wallet_id=cash.wallet_id),
        }
        return render(request, 'wallet.html', context=context)

@login_required
def shoppinglist(request):
    if request.method == 'POST':
        if request.POST['method'] == 'create':
            shoppinglist = ShoppingList()
            shoppinglist.user = request.user
            shoppinglist.shoppinglist_note = request.POST['shoppinglist_note']
            try:
                request.POST['shoppinglist_isDone']
                shoppinglist.shoppinglist_isDone = True
            except:
                shoppinglist.shoppinglist_isDone = False
            try:
                shoppinglist.category = Category.objects.get(category_id=request.POST['category'], user_id=request.user.id)
            except:
                shoppinglist.category = None
            shoppinglist.save()
        elif request.POST['method'] == 'delete':
            shoppinglist = ShoppingList.objects.get(shoppinglist_id=request.POST['shoppinglist_id'], user_id=request.user.id)
            shoppinglist.delete()
        elif request.POST['method'] == 'update':
            shoppinglist = ShoppingList.objects.get(shoppinglist_id=request.POST['shoppinglist_id'], user_id=request.user.id)
            shoppinglist.shoppinglist_note = request.POST['shoppinglist_note']
            try:
                request.POST['shoppinglist_isDone']
                shoppinglist.shoppinglist_isDone = True
            except:
                shoppinglist.shoppinglist_isDone = False
            try:
                shoppinglist.category = Category.objects.get(category_id=request.POST['category'], user_id=request.user.id)
            except:
                shoppinglist.category = None
            shoppinglist.save()
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        context = {
            'categories': Category.objects.filter(user=request.user),
            'shoppinglists': ShoppingList.objects.filter(user=request.user),
        }
        return render(request, 'shoppinglist.html', context=context)




