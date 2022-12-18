import datetime
import json
import random

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from .models import Card, Payment


def index(request):
    return render(request, 'cards/index.html')


def registration(request):
    if request.method == 'POST':
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('catalog')
            except IntegrityError:
                return render(
                    request,
                    'cards/registration.html',
                    {
                        'form': UserCreationForm(),
                        'error_name': f'''Пользователь с именем {request.POST["username"]} уже зарегистрирован. 
                                            Введите другое имя '''
                    }
                )
        else:
            return render(
                request,
                'cards/registration.html',
                {'form': UserCreationForm(), 'error_pass': 'Пароли не совпадают. Введите данные заново'}
            )

    return render(request, 'cards/registration.html', {'form': UserCreationForm()})


def login_user(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(
                request,
                'cards/login.html',
                {'form': AuthenticationForm(), 'error': 'Неверная пара имя - пароль'}
            )
        else:
            login(request, user)
            return redirect('home')

    return render(request, 'cards/login.html', {'form': AuthenticationForm()})


@login_required
def logout_user(request):
    logout(request)
    return redirect('home')


@login_required
def card_list(request):
    cards = Card.objects.all().filter(user=request.user)
    return render(request, 'cards/cards.html', {'cards': cards})


@login_required
def card_page(request, card_pk):
    card = Card.objects.get(pk=card_pk)
    payments = Payment.objects.all().filter(card=card_pk)
    return render(request, 'cards/card.html', {'card': card, 'payments': payments})


@login_required
def activity(request):
    if request.method == 'POST':
        card_pk = json.loads(request.body.decode())['card_pk']
        current_card = Card.objects.get(pk=card_pk)

        if current_card._status == 'active':
            current_card.status = 'n-active'
        elif current_card._status == 'n-active':
            current_card.status = 'active'
        current_card.save()
        response = HttpResponse()

        response['body'] = 'activity is changed'
        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


@login_required
def search(request):
    query_string = request.POST['search']
    cards_user = Card.objects.all().filter(user=request.user)
    series_result = cards_user.filter(series__contains=query_string)
    number_result = cards_user.filter(number__contains=query_string)
    release_date_result = cards_user.filter(release_date__contains=query_string)
    end_activity_result = cards_user.filter(end_activity__contains=query_string)
    status_result = []
    if query_string in 'активирована':
        status_result.extend(cards_user.filter(_status='active'))
    elif query_string in 'не активирована':
        status_result.extend(cards_user.filter(_status='n-active'))
    elif query_string in 'просрочена':
        status_result.extend(cards_user.filter(_status='over'))

    search_result = set([*series_result, *number_result, *release_date_result, *end_activity_result, *status_result])
    return render(
        request,
        'cards/cards.html',
        {'cards': search_result, 'len': len(search_result), 'query_string': query_string}
    )


def delete(request):
    if request.method == 'POST':
        card_pk = json.loads(request.body.decode())['card_pk']
        current_card = Card.objects.get(pk=card_pk)
        current_card.delete()
        return HttpResponse()


@login_required
def generate(request):
    if request.method == 'POST':
        print(request.POST)
        current_series = request.POST['series']
        days_delta = int(request.POST['activity'])
        for _ in range(int(request.POST['card_amount'])):
            new_card = Card(
                user=request.user,
                series=current_series,
                number=random.randint(100000, 999999999999),
                release_date=timezone.now(),
                end_activity=timezone.now() + datetime.timedelta(days=days_delta)
            )
            new_card.save()
        return redirect('cards')
    return render(request, 'cards/generate.html')
