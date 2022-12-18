from django.contrib import admin

from .models import Card, Payment


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    model = Card
    inlines = PaymentInline,

