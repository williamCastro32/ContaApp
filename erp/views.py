from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Client, MerchandiseEntry, Purchase, Sale, Expense, AccountReceivable, Payment
from .forms import ClientForm, MerchandiseEntryForm, PurchaseForm, SaleForm, ExpenseForm, AccountReceivableForm, PaymentForm

# Client Views
class ClientListView(ListView):
    model = Client
    template_name = 'client_list.html'
    context_object_name = 'clients'

class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'client_form.html'
    success_url = reverse_lazy('client-list')

class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'client_form.html'
    success_url = reverse_lazy('client-list')

class ClientDeleteView(DeleteView):
    model = Client
    template_name = 'client_confirm_delete.html'
    success_url = reverse_lazy('client-list')

# MerchandiseEntry Views
class MerchandiseEntryListView(ListView):
    model = MerchandiseEntry
    template_name = 'merchandise_entry_list.html'
    context_object_name = 'merchandise_entries'

class MerchandiseEntryCreateView(CreateView):
    model = MerchandiseEntry
    form_class = MerchandiseEntryForm
    template_name = 'merchandise_entry_form.html'
    success_url = reverse_lazy('merchandise-list')

class MerchandiseEntryUpdateView(UpdateView):
    model = MerchandiseEntry
    form_class = MerchandiseEntryForm
    template_name = 'merchandise_entry_form.html'
    success_url = reverse_lazy('merchandise-list')

class MerchandiseEntryDeleteView(DeleteView):
    model = MerchandiseEntry
    template_name = 'merchandise_entry_confirm_delete.html'
    success_url = reverse_lazy('merchandise-list')

# Purchase Views
class PurchaseListView(ListView):
    model = Purchase
    template_name = 'purchase_list.html'
    context_object_name = 'purchases'

class PurchaseCreateView(CreateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'purchase_form.html'
    success_url = reverse_lazy('purchase-list')

class PurchaseUpdateView(UpdateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'purchase_form.html'
    success_url = reverse_lazy('purchase-list')

class PurchaseDeleteView(DeleteView):
    model = Purchase
    template_name = 'purchase_confirm_delete.html'
    success_url = reverse_lazy('purchase-list')

# Sale Views
class SaleListView(ListView):
    model = Sale
    template_name = 'sale_list.html'
    context_object_name = 'sales'

class SaleCreateView(CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sale_form.html'
    success_url = reverse_lazy('sale-list')

class SaleUpdateView(UpdateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sale_form.html'
    success_url = reverse_lazy('sale-list')

class SaleDeleteView(DeleteView):
    model = Sale
    template_name = 'sale_confirm_delete.html'
    success_url = reverse_lazy('sale-list')

# Expense Views
class ExpenseListView(ListView):
    model = Expense
    template_name = 'expense_list.html'
    context_object_name = 'expenses'

class ExpenseCreateView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expense_form.html'
    success_url = reverse_lazy('expense-list')

class ExpenseUpdateView(UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expense_form.html'
    success_url = reverse_lazy('expense-list')

class ExpenseDeleteView(DeleteView):
    model = Expense
    template_name = 'expense_confirm_delete.html'
    success_url = reverse_lazy('expense-list')

# AccountReceivable Views
class AccountReceivableListView(ListView):
    model = AccountReceivable
    template_name = 'account_receivable_list.html'
    context_object_name = 'account_receivables'

class AccountReceivableCreateView(CreateView):
    model = AccountReceivable
    form_class = AccountReceivableForm
    template_name = 'account_receivable_form.html'
    success_url = reverse_lazy('account-receivable-list')

class AccountReceivableUpdateView(UpdateView):
    model = AccountReceivable
    form_class = AccountReceivableForm
    template_name = 'account_receivable_form.html'
    success_url = reverse_lazy('account-receivable-list')

class AccountReceivableDeleteView(DeleteView):
    model = AccountReceivable
    template_name = 'account_receivable_confirm_delete.html'
    success_url = reverse_lazy('account-receivable-list')

# Payment Views
class PaymentListView(ListView):
    model = Payment
    template_name = 'payment_list.html'
    context_object_name = 'payments'

class PaymentCreateView(CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payment_form.html'
    success_url = reverse_lazy('payment-list')

class PaymentUpdateView(UpdateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'payment_form.html'
    success_url = reverse_lazy('payment-list')

class PaymentDeleteView(DeleteView):
    model = Payment
    template_name = 'payment_confirm_delete.html'
    success_url = reverse_lazy('payment-list')
