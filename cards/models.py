import datetime

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    series = models.CharField(max_length=6)
    number = models.PositiveIntegerField(validators=[MaxValueValidator(999999999999), MinValueValidator(100000)])
    release_date = models.DateTimeField()
    end_activity = models.DateTimeField()

    STATUS_CHOICES = [
        ('active', 'активирована'),
        ('n-active', 'не активирована'),
        ('over', 'просрочена')
    ]
    _status = models.CharField(choices=STATUS_CHOICES, default='n-active', max_length=13)

    @property
    def status(self):
        if timezone.now() > self.end_activity:
            self._status = 'over'
            self.save()
        return self.get__status_display

    @status.setter
    def status(self, new):
        self._status = new
        self.save()


class Payment(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    pay_date = models.DateTimeField()
    amount = models.DecimalField(decimal_places=2, max_digits=20)
