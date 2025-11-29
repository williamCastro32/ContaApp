from decimal import Decimal
from django.contrib import admin
from django.db.models import Sum, F
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Supplier, Client, Product, ProductCostHistory,
    Purchase, PurchaseItem, PurchaseExpense,
    Sale, SaleItem, SaleExpense,
    Payment, PaymentAllocation
)


# -------------------------------------------------------------------------
# INLINES
# -------------------------------------------------------------------------
class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    fields = ('product', 'quantity', 'unit_price', 'get_total')
    readonly_fields = ('get_total',)
    autocomplete_fields = ['product']
    
    def get_total(self, obj):
        if obj.pk:
            return f"${obj.get_total():,.2f}"
        return "-"
    get_total.short_description = "Total"


class PurchaseExpenseInline(admin.TabularInline):
    model = PurchaseExpense
    extra = 1
    fields = ('description', 'amount')


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    fields = ('product', 'quantity', 'unit_price', 'get_total')
    readonly_fields = ('get_total',)
    autocomplete_fields = ['product']
    
    def get_total(self, obj):
        if obj.pk:
            return f"${obj.get_total():,.2f}"
        return "-"
    get_total.short_description = "Total"


class SaleExpenseInline(admin.TabularInline):
    model = SaleExpense
    extra = 1
    fields = ('description', 'amount')


class PaymentAllocationInline(admin.TabularInline):
    model = PaymentAllocation
    extra = 1
    fields = ('sale', 'amount', 'get_sale_balance')
    readonly_fields = ('get_sale_balance',)
    autocomplete_fields = ['sale']
    
    def get_sale_balance(self, obj):
        if obj.pk:
            balance = obj.sale.get_balance()
            color = 'red' if balance > 0 else 'green'
            return format_html(
                '<span style="color: {};">${:,.2f}</span>',
                color, balance
            )
        return "-"
    get_sale_balance.short_description = "Saldo Venta"


class ProductCostHistoryInline(admin.TabularInline):
    model = ProductCostHistory
    extra = 0
    fields = ('date', 'cost', 'source')
    readonly_fields = ('date', 'cost', 'source')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


# -------------------------------------------------------------------------
# SUPPLIER
# -------------------------------------------------------------------------
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'get_total_purchases', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('name', 'contact_info')
    ordering = ('name',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'contact_info', 'active')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def get_total_purchases(self, obj):
        count = obj.purchases.filter(status=Purchase.Status.COMPLETED).count()
        return f"{count} compras"
    get_total_purchases.short_description = "Compras"


# -------------------------------------------------------------------------
# CLIENT
# -------------------------------------------------------------------------
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'get_total_sales', 'get_debt', 'created_at')
    list_filter = ('active', 'created_at')
    search_fields = ('name', 'contact_info')
    ordering = ('name',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'contact_info', 'active')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    
    def get_total_sales(self, obj):
        count = obj.sales.filter(status=Sale.Status.COMPLETED).count()
        return f"{count} ventas"
    get_total_sales.short_description = "Ventas"
    
    def get_debt(self, obj):
        debt = obj.get_total_debt()
        if debt > 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">${:,.2f}</span>',
                debt
            )
        return format_html('<span style="color: green;">$0.00</span>')
    get_debt.short_description = "Deuda Total"


# -------------------------------------------------------------------------
# PRODUCT
# -------------------------------------------------------------------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'unit_type', 'get_stock_display', 'reference_price', 
        'get_last_cost', 'active'
    )
    list_filter = ('unit_type', 'active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('name', 'description', 'unit_type', 'active')
        }),
        ('Stock e Inventario', {
            'fields': ('stock', 'min_stock', 'reference_price')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductCostHistoryInline]
    
    def get_stock_display(self, obj):
        is_low = obj.is_low_stock()
        color = 'red' if is_low else 'green'
        icon = '⚠️' if is_low else '✓'
        return format_html(
            '<span style="color: {};">{} {:.3f} {}</span>',
            color, icon, obj.stock, obj.get_unit_type_display()
        )
    get_stock_display.short_description = "Stock"
    
    def get_last_cost(self, obj):
        cost = obj.get_last_purchase_cost()
        if cost > 0:
            return f"${cost:,.2f}"
        return "-"
    get_last_cost.short_description = "Último Costo"


# -------------------------------------------------------------------------
# PURCHASE
# -------------------------------------------------------------------------
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        'folio', 'supplier', 'date', 'get_status_display', 
        'get_total_display', 'created_by', 'created_at'
    )
    list_filter = ('status', 'date', 'supplier', 'created_at')
    search_fields = ('folio', 'supplier__name', 'notes')
    ordering = ('-date', '-id')
    date_hierarchy = 'date'
    autocomplete_fields = ['supplier']
    
    fieldsets = (
        ('Información General', {
            'fields': ('folio', 'supplier', 'date', 'status')
        }),
        ('Detalles', {
            'fields': ('notes',)
        }),
        ('Totales', {
            'fields': ('get_total_items_display', 'get_total_expenses_display', 'get_total_display'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = (
        'folio', 'get_total_items_display', 'get_total_expenses_display',
        'get_total_display', 'created_at', 'updated_at'
    )
    inlines = [PurchaseItemInline, PurchaseExpenseInline]
    
    actions = ['mark_as_completed', 'mark_as_cancelled']
    
    def get_status_display(self, obj):
        colors = {
            'PENDING': 'orange',
            'COMPLETED': 'green',
            'CANCELLED': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    get_status_display.short_description = "Estado"
    
    def get_total_items_display(self, obj):
        if obj.pk:
            return f"${obj.get_total_items():,.2f}"
        return "$0.00"
    get_total_items_display.short_description = "Total Items"
    
    def get_total_expenses_display(self, obj):
        if obj.pk:
            return f"${obj.get_total_expenses():,.2f}"
        return "$0.00"
    get_total_expenses_display.short_description = "Total Gastos"
    
    def get_total_display(self, obj):
        if obj.pk:
            return format_html(
                '<strong style="color: green; font-size: 14px;">${:,.2f}</strong>',
                obj.get_total()
            )
        return "$0.00"
    get_total_display.short_description = "TOTAL"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def mark_as_completed(self, request, queryset):
        updated = 0
        for purchase in queryset:
            if purchase.status != Purchase.Status.COMPLETED:
                purchase.complete()
                updated += 1
        self.message_user(request, f"{updated} compra(s) marcada(s) como completada(s).")
    mark_as_completed.short_description = "Marcar como Completadas"
    
    def mark_as_cancelled(self, request, queryset):
        updated = 0
        for purchase in queryset:
            try:
                purchase.cancel()
                updated += 1
            except Exception as e:
                self.message_user(request, f"Error al cancelar {purchase.folio}: {str(e)}", level='error')
        if updated > 0:
            self.message_user(request, f"{updated} compra(s) cancelada(s).")
    mark_as_cancelled.short_description = "Cancelar Compras"


# -------------------------------------------------------------------------
# SALE
# -------------------------------------------------------------------------
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'folio', 'client', 'date', 'get_status_display',
        'get_payment_status_display', 'get_total_display',
        'get_balance_display', 'due_date', 'created_by'
    )
    list_filter = ('status', 'payment_status', 'date', 'due_date', 'client')
    search_fields = ('folio', 'client__name', 'notes')
    ordering = ('-date', '-id')
    date_hierarchy = 'date'
    autocomplete_fields = ['client']
    
    fieldsets = (
        ('Información General', {
            'fields': ('folio', 'client', 'date', 'status', 'payment_status', 'due_date')
        }),
        ('Detalles', {
            'fields': ('notes',)
        }),
        ('Totales', {
            'fields': (
                'get_total_items_display', 'get_total_expenses_display',
                'get_total_display', 'get_paid_display', 'get_balance_display'
            ),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'updated_by', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = (
        'folio', 'get_total_items_display', 'get_total_expenses_display',
        'get_total_display', 'get_paid_display', 'get_balance_display',
        'created_at', 'updated_at'
    )
    inlines = [SaleItemInline, SaleExpenseInline]
    
    actions = ['mark_as_completed', 'mark_as_cancelled']
    
    def get_status_display(self, obj):
        colors = {
            'PENDING': 'orange',
            'COMPLETED': 'green',
            'CANCELLED': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    get_status_display.short_description = "Estado"
    
    def get_payment_status_display(self, obj):
        colors = {
            'PAID': 'green',
            'CREDIT': 'orange',
            'CANCELLED': 'red'
        }
        icon = '✓' if obj.payment_status == 'PAID' else '⏱️' if obj.payment_status == 'CREDIT' else '✗'
        
        overdue = ''
        if obj.payment_status == 'CREDIT' and obj.is_overdue():
            overdue = ' ⚠️ VENCIDA'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}{}</span>',
            colors.get(obj.payment_status, 'black'),
            icon,
            obj.get_payment_status_display(),
            overdue
        )
    get_payment_status_display.short_description = "Estado Pago"
    
    def get_total_items_display(self, obj):
        if obj.pk:
            return f"${obj.get_total_items():,.2f}"
        return "$0.00"
    get_total_items_display.short_description = "Total Items"
    
    def get_total_expenses_display(self, obj):
        if obj.pk:
            return f"${obj.get_total_expenses():,.2f}"
        return "$0.00"
    get_total_expenses_display.short_description = "Total Gastos"
    
    def get_total_display(self, obj):
        if obj.pk:
            return format_html(
                '<strong style="color: blue; font-size: 14px;">${:,.2f}</strong>',
                obj.get_total()
            )
        return "$0.00"
    get_total_display.short_description = "TOTAL"
    
    def get_paid_display(self, obj):
        if obj.pk:
            paid = obj.get_amount_paid()
            return format_html(
                '<span style="color: green;">${:,.2f}</span>',
                paid
            )
        return "$0.00"
    get_paid_display.short_description = "Pagado"
    
    def get_balance_display(self, obj):
        if obj.pk:
            balance = obj.get_balance()
            color = 'red' if balance > 0 else 'green'
            return format_html(
                '<strong style="color: {}; font-size: 14px;">${:,.2f}</strong>',
                color, balance
            )
        return "$0.00"
    get_balance_display.short_description = "SALDO"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def mark_as_completed(self, request, queryset):
        updated = 0
        for sale in queryset:
            if sale.status != Sale.Status.COMPLETED:
                sale.complete()
                updated += 1
        self.message_user(request, f"{updated} venta(s) marcada(s) como completada(s).")
    mark_as_completed.short_description = "Marcar como Completadas"
    
    def mark_as_cancelled(self, request, queryset):
        updated = 0
        for sale in queryset:
            try:
                if sale.get_amount_paid() > 0:
                    self.message_user(
                        request,
                        f"No se puede cancelar {sale.folio}: tiene pagos asignados",
                        level='error'
                    )
                    continue
                sale.status = Sale.Status.CANCELLED
                sale.save()
                updated += 1
            except Exception as e:
                self.message_user(request, f"Error al cancelar {sale.folio}: {str(e)}", level='error')
        if updated > 0:
            self.message_user(request, f"{updated} venta(s) cancelada(s).")
    mark_as_cancelled.short_description = "Cancelar Ventas"


# -------------------------------------------------------------------------
# PAYMENT
# -------------------------------------------------------------------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client', 'date', 'get_amount_display',
        'get_allocated_display', 'get_available_display', 'created_by'
    )
    list_filter = ('date', 'client', 'created_at')
    search_fields = ('id', 'client__name', 'notes')
    ordering = ('-date', '-id')
    date_hierarchy = 'date'
    autocomplete_fields = ['client']
    
    fieldsets = (
        ('Información General', {
            'fields': ('client', 'date', 'amount')
        }),
        ('Detalles', {
            'fields': ('notes',)
        }),
        ('Resumen', {
            'fields': ('get_allocated_display', 'get_available_display'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('get_allocated_display', 'get_available_display', 'created_at')
    inlines = [PaymentAllocationInline]
    
    def get_amount_display(self, obj):
        return format_html(
            '<strong style="color: blue;">${:,.2f}</strong>',
            obj.amount
        )
    get_amount_display.short_description = "Monto"
    
    def get_allocated_display(self, obj):
        if obj.pk:
            allocated = obj.total_allocated()
            return format_html(
                '<span style="color: green;">${:,.2f}</span>',
                allocated
            )
        return "$0.00"
    get_allocated_display.short_description = "Asignado"
    
    def get_available_display(self, obj):
        if obj.pk:
            available = obj.unallocated_amount()
            color = 'red' if available > 0 else 'green'
            return format_html(
                '<strong style="color: {};">${:,.2f}</strong>',
                color, available
            )
        return "$0.00"
    get_available_display.short_description = "Disponible"
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# -------------------------------------------------------------------------
# PAYMENT ALLOCATION
# -------------------------------------------------------------------------
@admin.register(PaymentAllocation)
class PaymentAllocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_payment_link', 'get_sale_link', 'amount', 'created_at')
    list_filter = ('created_at', 'payment__client')
    search_fields = ('payment__id', 'sale__folio', 'payment__client__name')
    ordering = ('-created_at',)
    autocomplete_fields = ['payment', 'sale']
    
    fieldsets = (
        ('Asignación', {
            'fields': ('payment', 'sale', 'amount')
        }),
        ('Información', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
    
    def get_payment_link(self, obj):
        url = reverse('admin:core_payment_change', args=[obj.payment.id])
        return format_html('<a href="{}">{}</a>', url, f"Pago #{obj.payment.id}")
    get_payment_link.short_description = "Pago"
    
    def get_sale_link(self, obj):
        url = reverse('admin:core_sale_change', args=[obj.sale.id])
        return format_html('<a href="{}">{}</a>', url, obj.sale.folio)
    get_sale_link.short_description = "Venta"


# -------------------------------------------------------------------------
# PRODUCT COST HISTORY
# -------------------------------------------------------------------------
@admin.register(ProductCostHistory)
class ProductCostHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'cost', 'date', 'source', 'created_at')
    list_filter = ('source', 'date', 'created_at')
    search_fields = ('product__name',)
    ordering = ('-date', '-id')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Información', {
            'fields': ('product', 'cost', 'date', 'source')
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        # Solo se crean automáticamente desde compras
        return False