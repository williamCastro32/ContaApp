from django.contrib import admin
from .models import Client, MerchandiseEntry, Purchase, Sale, Expense, AccountReceivable, Payment

admin.site.register(Client)
admin.site.register(MerchandiseEntry)
admin.site.register(Purchase)
admin.site.register(Sale)
admin.site.register(Expense)
admin.site.register(AccountReceivable)
admin.site.register(Payment)
