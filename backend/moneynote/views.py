from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Transaction, Category, Wallet, ShoppingList
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.db.models import Sum
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError


def index(request):
    if request.user.is_authenticated:
        # Retrieve transactions, categories, wallets, and shopping lists for the current user
        transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_date')
        incomes = transactions.filter(transaction_nominal__gt=0)
        expenses = transactions.filter(transaction_nominal__lt=0)
        categories = Category.objects.filter(user=request.user)
        wallets = Wallet.objects.filter(user=request.user)
        shopping_lists = ShoppingList.objects.filter(user=request.user)
        # Calculate the total wallet balance
        saldo = wallets.aggregate(total=Sum('wallet_saldo'))['total']
        # Pass the data to the template as a context
        context = {
            'incomes': incomes,
            'expenses': expenses,
            'categories': categories,
            'wallets': wallets,
            'saldo': saldo,
            'shoppinglists': shopping_lists,
        }
        return render(request, 'index.html', context)
    else:
        return render(request, 'landing.html')


def registerview(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                # Create and save a new user
                user = form.save()
                # Create a new wallet for the user with a default name and balance of 0
                Wallet.objects.create(
                    user=user,
                    wallet_name='Cash',
                    wallet_saldo=0,
                )
                # Authenticate and log in the user
                login(request, user)
                return redirect('index')
            else:
                # Extract any error messages from the form and pass them to the template
                message = ''
                for error in form.errors.values():
                    message += error[0] + ' '
                context = {'message': message}
                return render(request, 'register.html', context)
        else:
            return render(request, 'register.html')


def loginview(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('index')
            else:
                context = {'message': 'Invalid username or password.'}
                return render(request, 'login.html', context)
        else:
            # Check for special query string parameters in the request URL
            # and set the corresponding message to display to the user
            if 'delete' in request.GET:
                message = 'Account deleted.'
            elif 'password' in request.GET:
                message = 'Password changed.'
            else:
                message = ''
            context = {'message': message}
            return render(request, 'login.html', context)


def logoutview(request):
    # Check if the user is authenticated before logging them out
    if request.user.is_authenticated:
        logout(request)
    # Redirect the user to the login page regardless of whether they were
    # logged in or not
    return redirect('login')


@login_required
def setting(request):
    if request.method == 'POST':
        if request.POST['method'] == 'change_password':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                return redirect(reverse('login') + '?password=1')
            else:
                # Extract any error messages from the form and pass them to the template
                message = ''
                for error in form.errors.values():
                    message += error[0] + ' '
                context = {'message': message}
                return render(request, 'setting.html', context)
        elif request.POST['method'] == 'delete_account':
            username = request.user.username
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user:
                user.delete()
                return redirect(reverse('login') + '?delete=1')
            else:
                context = {'message': 'Invalid password'}
                return render(request, 'setting.html', context)
    else:
        return render(request, 'setting.html')

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
        # Create a new Transaction object and save it to the database
        transaction = Transaction(
            user=request.user,
            transaction_note=note,
            transaction_nominal=nominal,
            transaction_date=date,
            category_id=category,
            wallet_id=wallet,
        )
        transaction.save()
        # Update the wallet balance
        wallet = Wallet.objects.get(wallet_id=wallet)
        wallet.wallet_saldo += nominal
        wallet.save()
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        # Retrieve transactions, categories, and wallets for the current user
        transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_date')
        incomes = transactions.filter(transaction_nominal__gt=0)
        expenses = transactions.filter(transaction_nominal__lt=0)
        categories = Category.objects.filter(user=request.user)
        wallets = Wallet.objects.filter(user=request.user)
        # Pass the data to the template as a context
        context = {
            'incomes': incomes,
            'expenses': expenses,
            'categories': categories,
            'wallets': wallets,
        }
        return render(request, 'transaction.html', context)



@login_required
def transaction_detail(request, id):
    try:
        transaction = Transaction.objects.get(transaction_id=id, user=request.user)
    except Transaction.DoesNotExist:
        raise Http404()

    if request.method == 'POST':
        if request.POST['method'] == 'update':
            transaction.transaction_note = request.POST['note']
            transaction.transaction_date = request.POST['date']
            wallet_id = request.POST['wallet']
            category_id = request.POST['category']
            wallet = Wallet.objects.get(wallet_id=transaction.wallet_id)
            wallet.wallet_saldo -= transaction.transaction_nominal
            if request.POST['type'] == 'income':
                nominal = int(request.POST['nominal'])
            else:
                nominal = int(request.POST['nominal']) * -1
            transaction.transaction_nominal = nominal
            wallet.wallet_saldo += transaction.transaction_nominal
            wallet.save()
            try:
                transaction.category = Category.objects.get(user=request.user, category_id=category_id)
            except ValueError:
                transaction.category = None
            wallet = Wallet.objects.get(user=request.user, wallet_id=wallet_id)
            transaction.wallet = wallet
            transaction.save()
            return redirect(request.META.get('HTTP_REFERER'))
        elif request.POST['method'] == 'updateandexit':
            transaction.transaction_note = request.POST['note']
            transaction.transaction_date = request.POST['date']
            wallet_id = request.POST['wallet']
            category_id = request.POST['category']
            wallet = Wallet.objects.get(wallet_id=transaction.wallet_id)
            wallet.wallet_saldo -= transaction.transaction_nominal
            if request.POST['type'] == 'income':
                nominal = int(request.POST['nominal'])
            else:
                nominal = int(request.POST['nominal']) * -1
            transaction.transaction_nominal = nominal
            wallet.wallet_saldo += transaction.transaction_nominal
            wallet.save()
            try:
                transaction.category = Category.objects.get(user=request.user, category_id=category_id)
            except ValueError:
                transaction.category = None
            wallet = Wallet.objects.get(user=request.user, wallet_id=wallet_id)
            transaction.wallet = wallet
            transaction.save()
            return redirect('transaction')
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
        return render(request, 'transaction_detail.html', context)


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
            Transaction.objects.filter(category=category).update(category=None)
            ShoppingList.objects.filter(category=category).update(category=None)
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
        return render(request, 'category.html', context)


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
            except MultiValueDictKeyError:
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
            except MultiValueDictKeyError:
                shoppinglist.shoppinglist_isDone = False
            try:
                shoppinglist.category = Category.objects.get(category_id=request.POST['category'], user_id=request.user.id)
            except ValueError:
                shoppinglist.category = None
            shoppinglist.save()
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        context = {
            'categories': Category.objects.filter(user=request.user),
            'shoppinglists': ShoppingList.objects.filter(user=request.user),
        }
        return render(request, 'shoppinglist.html', context)