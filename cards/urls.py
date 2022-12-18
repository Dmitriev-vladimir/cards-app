from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('registration/', views.registration, name='registration'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('cards/', views.card_list, name='cards'),
    path('card/<int:card_pk>/', views.card_page, name='card'),
    path('search/', views.search, name='search'),
    path('generate/', views.generate, name='generate'),
    path('activity/', views.activity),
    path('delete/', views.delete)
]
