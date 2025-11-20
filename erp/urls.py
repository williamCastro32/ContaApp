from django.urls import path
from .views import (
    ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView,
    MerchandiseEntryListView, MerchandiseEntryCreateView, MerchandiseEntryUpdateView, MerchandiseEntryDeleteView,
    PurchaseListView, PurchaseCreateView, PurchaseUpdateView, PurchaseDeleteView,
    SaleListView, SaleCreateView, SaleUpdateView, SaleDeleteView,
    ExpenseListView, ExpenseCreateView, ExpenseUpdateView, ExpenseDeleteView,
    AccountReceivableListView, AccountReceivableCreateView, AccountReceivableUpdateView, AccountReceivableDeleteView,
    PaymentListView, PaymentCreateView, PaymentUpdateView, PaymentDeleteView,
)

urlpatterns = [
    # Client URLs
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('clients/create/', ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/update/', ClientUpdateView.as_view(), name='client-update'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client-delete'),

    # MerchandiseEntry URLs
    path('merchandise/', MerchandiseEntryListView.as_view(), name='merchandise-list'),
    path('merchandise/create/', MerchandiseEntryCreateView.as_view(), name='merchandise-create'),
    path('merchandise/<int:pk>/update/', MerchandiseEntryUpdateView.as_view(), name='merchandise-update'),
    path('merchandise/<int:pk>/delete/', MerchandiseEntryDeleteView.as_view(), name='merchandise-delete'),

    # Purchase URLs
    path('purchases/', PurchaseListView.as_view(), name='purchase-list'),
    path('purchases/create/', PurchaseCreateView.as_view(), name='purchase-create'),
    path('purchases/<int:pk>/update/', PurchaseUpdateView.as_view(), name='purchase-update'),
    path('purchases/<int:pk>/delete/', PurchaseDeleteView.as_view(), name='purchase-delete'),

    # Sale URLs
    path('sales/', SaleListView.as_view(), name='sale-list'),
    path('sales/create/', SaleCreateView.as_view(), name='sale-create'),
    path('sales/<int:pk>/update/', SaleUpdateView.as_view(), name='sale-update'),
    path('sales/<int:pk>/delete/', SaleDeleteView.as_view(), name='sale-delete'),

    # Expense URLs
    path('expenses/', ExpenseListView.as_view(), name='expense-list'),
    path('expenses/create/', ExpenseCreateView.as_view(), name='expense-create'),
    path('expenses/<int:pk>/update/', ExpenseUpdateView.as_view(), name='expense-update'),
    path('expenses/<int:pk>/delete/', ExpenseDeleteView.as_view(), name='expense-delete'),

    # AccountReceivable URLs
    path('accounts-receivable/', AccountReceivableListView.as_view(), name='account-receivable-list'),
    path('accounts-receivable/create/', AccountReceivableCreateView.as_view(), name='account-receivable-create'),
    path('accounts-receivable/<int:pk>/update/', AccountReceivableUpdateView.as_view(), name='account-receivable-update'),
    path('accounts-receivable/<int:pk>/delete/', AccountReceivableDeleteView.as_view(), name='account-receivable-delete'),

    # Payment URLs
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('payments/create/', PaymentCreateView.as_view(), name='payment-create'),
    path('payments/<int:pk>/update/', PaymentUpdateView.as_view(), name='payment-update'),
    path('payments/<int:pk>/delete/', PaymentDeleteView.as_view(), name='payment-delete'),
]
