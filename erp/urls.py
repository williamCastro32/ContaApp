from django.urls import path
from .views import (
    SupplierListView, SupplierCreateView, SupplierUpdateView, SupplierDeleteView,
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView,
    ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView,
    PurchaseListView, PurchaseCreateView, PurchaseUpdateView, PurchaseDeleteView,
    SaleListView, SaleCreateView, SaleUpdateView, SaleDeleteView,
    PaymentListView, PaymentCreateView, PaymentUpdateView, PaymentDeleteView,
)

urlpatterns = [
    # Supplier URLs
    path('suppliers/', SupplierListView.as_view(), name='supplier-list'),
    path('suppliers/create/', SupplierCreateView.as_view(), name='supplier-create'),
    path('suppliers/<int:pk>/update/', SupplierUpdateView.as_view(), name='supplier-update'),
    path('suppliers/<int:pk>/delete/', SupplierDeleteView.as_view(), name='supplier-delete'),

    # Product URLs
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),

    # Client URLs
    path('clients/', ClientListView.as_view(), name='client-list'),
    path('clients/create/', ClientCreateView.as_view(), name='client-create'),
    path('clients/<int:pk>/update/', ClientUpdateView.as_view(), name='client-update'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client-delete'),

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

    # Payment URLs
    path('payments/', PaymentListView.as_view(), name='payment-list'),
    path('payments/create/', PaymentCreateView.as_view(), name='payment-create'),
    path('payments/<int:pk>/update/', PaymentUpdateView.as_view(), name='payment-update'),
    path('payments/<int:pk>/delete/', PaymentDeleteView.as_view(), name='payment-delete'),
]