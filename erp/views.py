from django.db import transaction
from django.forms import inlineformset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import (
    Supplier, Product, Client, Purchase, PurchaseItem, PurchaseExpense, Sale, SaleItem, Payment
)
from .forms import (
    SupplierForm, ProductForm, ClientForm, PurchaseForm, PurchaseItemForm, PurchaseExpenseForm, SaleForm, SaleItemForm, PaymentForm
)

# Supplier Views
class SupplierListView(ListView):
    model = Supplier
    template_name = 'supplier_list.html'
    context_object_name = 'suppliers'

class SupplierCreateView(CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'supplier_form.html'
    success_url = reverse_lazy('supplier-list')

class SupplierUpdateView(UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = 'supplier_form.html'
    success_url = reverse_lazy('supplier-list')

class SupplierDeleteView(DeleteView):
    model = Supplier
    template_name = 'supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier-list')

# Product Views
class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product-list')

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product_form.html'
    success_url = reverse_lazy('product-list')

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'product_confirm_delete.html'
    success_url = reverse_lazy('product-list')

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

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        PurchaseItemFormSet = inlineformset_factory(Purchase, PurchaseItem, form=PurchaseItemForm, extra=1, can_delete=True)
        if self.request.POST:
            data['item_formset'] = PurchaseItemFormSet(self.request.POST, prefix='items')
        else:
            data['item_formset'] = PurchaseItemFormSet(prefix='items')
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        item_formset = context['item_formset']
        with transaction.atomic():
            self.object = form.save()
            if item_formset.is_valid():
                item_formset.instance = self.object
                item_formset.save()
        return super().form_valid(form)

class PurchaseUpdateView(UpdateView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'purchase_form.html'
    success_url = reverse_lazy('purchase-list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        PurchaseItemFormSet = inlineformset_factory(Purchase, PurchaseItem, form=PurchaseItemForm, extra=1, can_delete=True)
        if self.request.POST:
            data['item_formset'] = PurchaseItemFormSet(self.request.POST, instance=self.object, prefix='items')
        else:
            data['item_formset'] = PurchaseItemFormSet(instance=self.object, prefix='items')
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        item_formset = context['item_formset']
        with transaction.atomic():
            self.object = form.save()
            if item_formset.is_valid():
                item_formset.instance = self.object
                item_formset.save()
        return super().form_valid(form)

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

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        SaleItemFormSet = inlineformset_factory(Sale, SaleItem, form=SaleItemForm, extra=1, can_delete=True)
        if self.request.POST:
            data['item_formset'] = SaleItemFormSet(self.request.POST, prefix='items')
        else:
            data['item_formset'] = SaleItemFormSet(prefix='items')
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        item_formset = context['item_formset']
        with transaction.atomic():
            self.object = form.save()
            if item_formset.is_valid():
                item_formset.instance = self.object
                item_formset.save()
        return super().form_valid(form)

class SaleUpdateView(UpdateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sale_form.html'
    success_url = reverse_lazy('sale-list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        SaleItemFormSet = inlineformset_factory(Sale, SaleItem, form=SaleItemForm, extra=1, can_delete=True)
        if self.request.POST:
            data['item_formset'] = SaleItemFormSet(self.request.POST, instance=self.object, prefix='items')
        else:
            data['item_formset'] = SaleItemFormSet(instance=self.object, prefix='items')
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        item_formset = context['item_formset']
        with transaction.atomic():
            self.object = form.save()
            if item_formset.is_valid():
                item_formset.instance = self.object
                item_formset.save()
        return super().form_valid(form)

class SaleDeleteView(DeleteView):
    model = Sale
    template_name = 'sale_confirm_delete.html'
    success_url = reverse_lazy('sale-list')

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