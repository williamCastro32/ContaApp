from django import forms
from .models import Client, MerchandiseEntry, Purchase, Sale, Expense, AccountReceivable, Payment

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = '__all__'
        labels = {
            'name': 'Nombre',
            'contact_info': 'Información de Contacto',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_info': forms.Textarea(attrs={'class': 'form-control'}),
        }

class MerchandiseEntryForm(forms.ModelForm):
    class Meta:
        model = MerchandiseEntry
        fields = '__all__'
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = '__all__'
        labels = {
            'merchandise_entry': 'Entrada de Mercancía',
            'purchase_date': 'Fecha de Compra',
            'supplier': 'Proveedor',
            'quantity': 'Cantidad',
            'unit_price': 'Precio Unitario',
        }
        widgets = {
            'merchandise_entry': forms.Select(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = '__all__'
        labels = {
            'merchandise_entry': 'Entrada de Mercancía',
            'client': 'Cliente',
            'sale_date': 'Fecha de Venta',
            'quantity': 'Cantidad',
            'unit_price': 'Precio Unitario',
        }
        widgets = {
            'merchandise_entry': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'sale_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = '__all__'
        labels = {
            'merchandise_entry': 'Entrada de Mercancía',
            'description': 'Descripción',
            'amount': 'Monto',
            'expense_date': 'Fecha de Gasto',
        }
        widgets = {
            'merchandise_entry': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'expense_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class AccountReceivableForm(forms.ModelForm):
    class Meta:
        model = AccountReceivable
        fields = '__all__'
        labels = {
            'sale': 'Venta',
            'amount': 'Monto',
            'due_date': 'Fecha de Vencimiento',
            'paid': 'Pagado',
        }
        widgets = {
            'sale': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'
        labels = {

            'account_receivable': 'Cuenta por Cobrar',
            'payment_date': 'Fecha de Pago',
            'amount': 'Monto',
        }
        widgets = {
            'account_receivable': forms.Select(attrs={'class': 'form-control'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
