from django.db import models
from django.conf import settings

class Client(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class MerchandiseEntry(models.Model):
    name = models.CharField(max_length=255)
    entry_date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Purchase(models.Model):
    merchandise_entry = models.ForeignKey(MerchandiseEntry, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateField()
    supplier = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Purchase of {self.quantity} for {self.merchandise_entry.name}"

class Sale(models.Model):
    merchandise_entry = models.ForeignKey(MerchandiseEntry, on_delete=models.CASCADE, related_name='sales')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sales')
    sale_date = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale of {self.quantity} to {self.client.name}"

class Expense(models.Model):
    merchandise_entry = models.ForeignKey(MerchandiseEntry, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()

    def __str__(self):
        return f"{self.description} - {self.amount}"

class AccountReceivable(models.Model):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, related_name='account_receivable')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"AR for sale to {self.sale.client.name} of {self.amount}"

class Payment(models.Model):
    account_receivable = models.ForeignKey(AccountReceivable, on_delete=models.CASCADE, related_name='payments')
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Payment of {self.amount} for {self.account_receivable}"
