from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Sum, F, Max
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property
import logging

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# UTILS
# -------------------------------------------------------------------------
def to_decimal(value, places=2):
    """Convierte a Decimal y normaliza a n decimales"""
    quantize_str = '0.' + '0' * places
    return Decimal(str(value)).quantize(Decimal(quantize_str))


def next_folio(prefix: str, model) -> str:
    """
    Genera un folio secuencial: PREFIX-YYYYMMDD-00001
    Usa Max() para obtener el último número del día y evitar duplicados.
    """
    date_str = timezone.now().strftime("%Y%m%d")
    folio_prefix = f"{prefix}-{date_str}"
    
    # Buscar el último folio del día
    last_folio = model.objects.filter(
        folio__startswith=folio_prefix
    ).aggregate(Max('folio'))['folio__max']
    
    if last_folio:
        try:
            # Extraer el número secuencial del último folio
            seq = int(last_folio.split('-')[-1]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    
    return f"{folio_prefix}-{seq:05d}"


# -------------------------------------------------------------------------
# PRODUCTOS, PROVEEDOR, CLIENTE
# -------------------------------------------------------------------------
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.name

    def get_total_debt(self):
        """Obtiene el saldo total pendiente del cliente"""
        sales = self.sales.filter(
            status=Sale.Status.COMPLETED,
            payment_status=Sale.PaymentStatus.CREDIT
        )
        total = Decimal('0.00')
        for sale in sales:
            total += sale.get_balance()
        return total


class Product(models.Model):
    UNIT_KG = 'KG'
    UNIT_UNIT = 'UNIT'
    UNIT_BOX = 'BOX'
    UNIT_BULTO = 'BULTO'
    UNIT_CHOICES = [
        (UNIT_KG, 'Kilogramo'),
        (UNIT_UNIT, 'Unidad'),
        (UNIT_BOX, 'Caja'),
        (UNIT_BULTO, 'Bulto'),
    ]

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    stock = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal('0.000'))
    unit_type = models.CharField(max_length=10, choices=UNIT_CHOICES, default=UNIT_KG)
    reference_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    min_stock = models.DecimalField(max_digits=14, decimal_places=3, default=Decimal('0.000'), 
                                     help_text="Stock mínimo para alertas")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['active']),
            models.Index(fields=['stock']),
        ]

    def __str__(self):
        return self.name

    def is_low_stock(self):
        """Verifica si el stock está por debajo del mínimo"""
        return self.stock < self.min_stock

    def get_last_purchase_cost(self):
        """Obtiene el último costo de compra"""
        last_item = self.purchase_items.select_related('purchase').filter(
            purchase__status=Purchase.Status.COMPLETED
        ).order_by('-purchase__date').first()
        return last_item.unit_price if last_item else Decimal('0.00')


# -------------------------------------------------------------------------
# TRANSACCIONES (ABSTRACT)
# -------------------------------------------------------------------------
class TransactionBase(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        COMPLETED = 'COMPLETED', 'Completada'
        CANCELLED = 'CANCELLED', 'Cancelada'

    folio = models.CharField(max_length=64, unique=True, blank=True, db_index=True)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="%(class)s_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="%(class)s_updated"
    )

    class Meta:
        abstract = True
        ordering = ['-date', '-id']

    def clean(self):
        """Validación de fechas"""
        if self.date and self.date > timezone.now().date():
            raise ValidationError("La fecha no puede ser futura.")

    def save(self, *args, **kwargs):
        self.clean()
        if not self.folio:
            prefix = self.__class__.__name__.upper()
            self.folio = next_folio(prefix, self.__class__)
        super().save(*args, **kwargs)


# -------------------------------------------------------------------------
# PURCHASE (COMPRA)
# -------------------------------------------------------------------------
class Purchase(TransactionBase):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')

    class Meta(TransactionBase.Meta):
        indexes = [
            models.Index(fields=['date', 'status']),
            models.Index(fields=['supplier', 'date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Compra {self.folio} - {self.supplier.name} - {self.date}"

    @classmethod
    def get_with_details(cls, pk):
        """Obtiene compra con todas las relaciones precargadas"""
        return cls.objects.select_related(
            'supplier', 'created_by', 'updated_by'
        ).prefetch_related(
            'items__product', 'expenses'
        ).get(pk=pk)

    def get_total_items(self):
        """Total de items de la compra"""
        result = self.items.aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )['total']
        return to_decimal(result or 0)

    def get_total_expenses(self):
        """Total de gastos adicionales"""
        result = self.expenses.aggregate(total=Sum('amount'))['total']
        return to_decimal(result or 0)

    def get_total(self):
        """Total general de la compra"""
        return to_decimal(self.get_total_items() + self.get_total_expenses())

    @cached_property
    def total(self):
        """Propiedad cacheada del total"""
        return self.get_total()

    def complete(self):
        """Marca la compra como completada"""
        if self.status != self.Status.COMPLETED:
            self.status = self.Status.COMPLETED
            self.save()
            logger.info(f"Compra {self.folio} completada")

    def cancel(self):
        """Cancela la compra y revierte el stock"""
        if self.status == self.Status.CANCELLED:
            return
        
        with transaction.atomic():
            # Revertir stock de todos los items
            for item in self.items.select_for_update():
                p = Product.objects.select_for_update().get(pk=item.product.pk)
                p.stock -= item.quantity
                if p.stock < 0:
                    raise ValidationError(
                        f"Cancelar esta compra dejaría stock negativo en {p.name}"
                    )
                p.save()
            
            self.status = self.Status.CANCELLED
            self.save()
            logger.info(f"Compra {self.folio} cancelada")


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='purchase_items')
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('purchase', 'product')
        indexes = [
            models.Index(fields=['product', 'purchase']),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity} @ {self.unit_price}"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")
        if self.unit_price < 0:
            raise ValidationError("El precio unitario no puede ser negativo.")

    def get_total(self):
        return to_decimal(self.quantity * self.unit_price)

    def save(self, *args, **kwargs):
        self.clean()
        with transaction.atomic():
            is_update = self.pk is not None
            old_quantity = Decimal('0.000')
            
            if is_update:
                old = PurchaseItem.objects.get(pk=self.pk)
                old_quantity = old.quantity
            
            diff = self.quantity - old_quantity
            
            super().save(*args, **kwargs)
            
            # Actualizar stock si hay cambio
            if diff != 0:
                p = Product.objects.select_for_update().get(pk=self.product.pk)
                p.stock = (p.stock or Decimal('0')) + diff
                p.save()
                logger.debug(
                    f"Stock actualizado para {p.name}: {diff:+.3f} "
                    f"(nuevo stock: {p.stock})"
                )

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            p = Product.objects.select_for_update().get(pk=self.product.pk)
            new_stock = p.stock - self.quantity
            
            if new_stock < 0:
                raise ValidationError(
                    f"Eliminar este item dejaría stock negativo en {p.name}. "
                    f"Stock actual: {p.stock}, Cantidad del item: {self.quantity}"
                )
            
            p.stock = new_stock
            p.save()
            super().delete(*args, **kwargs)
            logger.debug(f"Item eliminado, stock de {p.name} actualizado: {p.stock}")


class PurchaseExpense(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.amount}"

    def clean(self):
        if self.amount < 0:
            raise ValidationError("El monto no puede ser negativo.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


# -------------------------------------------------------------------------
# SALE (VENTA)
# -------------------------------------------------------------------------
class Sale(TransactionBase):
    class PaymentStatus(models.TextChoices):
        PAID = 'PAID', 'Pagada'
        CREDIT = 'CREDIT', 'A crédito'
        CANCELLED = 'CANCELLED', 'Cancelada'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='sales')
    payment_status = models.CharField(
        max_length=10, 
        choices=PaymentStatus.choices, 
        default=PaymentStatus.CREDIT
    )
    due_date = models.DateField(null=True, blank=True)

    class Meta(TransactionBase.Meta):
        indexes = [
            models.Index(fields=['date', 'status', 'payment_status']),
            models.Index(fields=['client', 'date']),
            models.Index(fields=['due_date']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Venta {self.folio} - {self.client.name} - {self.date}"

    @classmethod
    def get_with_details(cls, pk):
        """Obtiene venta con todas las relaciones precargadas"""
        return cls.objects.select_related(
            'client', 'created_by', 'updated_by'
        ).prefetch_related(
            'items__product', 'expenses', 'payments__allocations'
        ).get(pk=pk)

    def get_total_items(self):
        """Total de items vendidos"""
        result = self.items.aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )['total']
        return to_decimal(result or 0)

    def get_total_expenses(self):
        """Total de gastos adicionales"""
        result = self.expenses.aggregate(total=Sum('amount'))['total']
        return to_decimal(result or 0)

    def get_total(self):
        """Total general de la venta"""
        return to_decimal(self.get_total_items() + self.get_total_expenses())

    def get_amount_paid(self):
        """Monto total pagado en esta venta"""
        result = self.allocations.aggregate(total=Sum('amount'))['total']
        return to_decimal(result or 0)

    def get_balance(self):
        """Saldo pendiente de pago"""
        return to_decimal(self.get_total() - self.get_amount_paid())

    @cached_property
    def total(self):
        return self.get_total()

    @cached_property
    def balance(self):
        return self.get_balance()

    def is_overdue(self):
        """Verifica si la venta está vencida"""
        if not self.due_date or self.payment_status != self.PaymentStatus.CREDIT:
            return False
        return timezone.now().date() > self.due_date

    def save(self, *args, **kwargs):
        """Detectar cambio a CANCELLED y validar/revertir stock"""
        self.clean()
        
        with transaction.atomic():
            is_update = self.pk is not None
            old_status = None
            
            if is_update:
                old = Sale.objects.select_for_update().get(pk=self.pk)
                old_status = old.status
                
                # Validar cancelación con pagos asignados
                if (old_status != self.status and 
                    self.status == self.Status.CANCELLED):
                    
                    if self.get_amount_paid() > 0:
                        raise ValidationError(
                            "No se puede cancelar una venta con pagos asignados. "
                            "Elimine primero las asignaciones de pago."
                        )
            
            super().save(*args, **kwargs)
            
            # Revertir stock si se cancela
            if is_update and old_status != self.status and self.status == self.Status.CANCELLED:
                for item in self.items.select_for_update():
                    p = Product.objects.select_for_update().get(pk=item.product.pk)
                    p.stock += item.quantity
                    p.save()
                
                # Actualizar estado de pago
                self.payment_status = self.PaymentStatus.CANCELLED
                Sale.objects.filter(pk=self.pk).update(
                    payment_status=self.PaymentStatus.CANCELLED
                )
                logger.info(f"Venta {self.folio} cancelada y stock revertido")

    def complete(self):
        """Marca la venta como completada"""
        if self.status != self.Status.COMPLETED:
            self.status = self.Status.COMPLETED
            self.save()
            logger.info(f"Venta {self.folio} completada")


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.DecimalField(max_digits=14, decimal_places=3)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('sale', 'product')
        indexes = [
            models.Index(fields=['product', 'sale']),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity} @ {self.unit_price}"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor a 0.")
        if self.unit_price < 0:
            raise ValidationError("El precio unitario no puede ser negativo.")

    def get_total(self):
        return to_decimal(self.quantity * self.unit_price)

    def save(self, *args, **kwargs):
        """
        Actualiza stock del producto al crear/modificar item.
        Valida stock disponible y estado de la venta.
        """
        self.clean()
        
        with transaction.atomic():
            # Lock del producto y venta
            p = Product.objects.select_for_update().get(pk=self.product.pk)
            sale = Sale.objects.select_for_update().get(pk=self.sale_id) if self.sale_id else None
            
            # Validar que la venta no esté cancelada
            if sale and sale.status == Sale.Status.CANCELLED:
                raise ValidationError(
                    "No se pueden modificar items de una venta cancelada."
                )
            
            is_update = self.pk is not None
            old_quantity = Decimal('0.000')
            
            if is_update:
                old = SaleItem.objects.get(pk=self.pk)
                old_quantity = old.quantity
            
            # Diferencia neta que se resta del stock
            diff = self.quantity - old_quantity
            new_stock = p.stock - diff
            
            # Validar stock suficiente
            if new_stock < 0:
                raise ValidationError(
                    f"Stock insuficiente para {p.name}. "
                    f"Disponible: {p.stock}, Requerido adicional: {diff}, "
                    f"Faltante: {abs(new_stock)}"
                )
            
            super().save(*args, **kwargs)
            
            # Actualizar stock
            if diff != 0:
                p.stock = new_stock
                p.save()
                logger.debug(
                    f"Stock actualizado para {p.name}: {-diff:+.3f} "
                    f"(nuevo stock: {p.stock})"
                )

    def delete(self, *args, **kwargs):
        """Devuelve el stock al producto al eliminar el item"""
        with transaction.atomic():
            p = Product.objects.select_for_update().get(pk=self.product.pk)
            p.stock += self.quantity
            p.save()
            super().delete(*args, **kwargs)
            logger.debug(
                f"Item eliminado, stock de {p.name} restaurado: +{self.quantity} "
                f"(nuevo stock: {p.stock})"
            )


class SaleExpense(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.description} - {self.amount}"

    def clean(self):
        if self.amount < 0:
            raise ValidationError("El monto no puede ser negativo.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


# -------------------------------------------------------------------------
# PAGOS: Payment + PaymentAllocation
# -------------------------------------------------------------------------
class Payment(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    class Meta:
        ordering = ['-date', '-id']
        indexes = [
            models.Index(fields=['client', 'date']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"Pago {self.id} - {self.client.name} - {self.amount}"

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("El monto del pago debe ser mayor a 0.")
        if self.date and self.date > timezone.now().date():
            raise ValidationError("La fecha del pago no puede ser futura.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def total_allocated(self):
        """Total asignado a ventas"""
        result = self.allocations.aggregate(total=Sum('amount'))['total']
        return to_decimal(result or 0)

    def unallocated_amount(self):
        """Monto disponible para asignar"""
        return to_decimal(self.amount - self.total_allocated())

    @cached_property
    def available(self):
        """Propiedad cacheada del monto disponible"""
        return self.unallocated_amount()


class PaymentAllocation(models.Model):
    """
    Asigna una porción de un pago a una venta específica.
    Permite aplicar un pago a múltiples ventas.
    """
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='allocations')
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='allocations')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('payment', 'sale')
        indexes = [
            models.Index(fields=['payment', 'sale']),
            models.Index(fields=['sale']),
        ]

    def __str__(self):
        return f"Asignación: ${self.amount} de Pago {self.payment.id} a Venta {self.sale.folio}"

    def clean(self):
        """Validación de montos y disponibilidad"""
        if self.amount <= 0:
            raise ValidationError("El monto asignado debe ser mayor a 0.")
        
        # Calcular monto disponible en el pago
        available = self.payment.amount - self.payment.total_allocated()
        
        # Si es una actualización, recuperar el monto anterior
        if self.pk:
            try:
                old = PaymentAllocation.objects.get(pk=self.pk)
                available += old.amount
            except PaymentAllocation.DoesNotExist:
                pass
        
        # Validar que no exceda el disponible del pago
        if self.amount > available:
            raise ValidationError(
                f"El monto asignado ({self.amount}) excede el disponible del pago ({available}). "
                f"Pago total: {self.payment.amount}, "
                f"Ya asignado: {self.payment.total_allocated()}"
            )
        
        # Validar que no exceda el saldo de la venta
        sale_balance = self.sale.get_balance()
        
        # Si es actualización, sumar el monto anterior al balance
        if self.pk:
            try:
                old = PaymentAllocation.objects.get(pk=self.pk)
                sale_balance += old.amount
            except PaymentAllocation.DoesNotExist:
                pass
        
        if self.amount > sale_balance:
            raise ValidationError(
                f"El monto asignado ({self.amount}) excede el saldo de la venta ({sale_balance})."
            )
        
        # Validar que la venta no esté cancelada
        if self.sale.status == Sale.Status.CANCELLED:
            raise ValidationError("No se pueden asignar pagos a ventas canceladas.")

    def save(self, *args, **kwargs):
        self.clean()
        
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            # Actualizar estado de pago de la venta
            sale_balance = self.sale.get_balance()
            
            if sale_balance == Decimal('0.00'):
                # Venta completamente pagada
                if self.sale.payment_status != Sale.PaymentStatus.PAID:
                    Sale.objects.filter(pk=self.sale.pk).update(
                        payment_status=Sale.PaymentStatus.PAID
                    )
                    logger.info(f"Venta {self.sale.folio} marcada como PAGADA")
            else:
                # Venta con saldo pendiente
                if self.sale.payment_status == Sale.PaymentStatus.PAID:
                    Sale.objects.filter(pk=self.sale.pk).update(
                        payment_status=Sale.PaymentStatus.CREDIT
                    )

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            sale = self.sale
            super().delete(*args, **kwargs)
            
            # Actualizar estado de pago si ahora tiene saldo
            sale_balance = sale.get_balance()
            if sale_balance > Decimal('0.00'):
                if sale.payment_status == Sale.PaymentStatus.PAID:
                    Sale.objects.filter(pk=sale.pk).update(
                        payment_status=Sale.PaymentStatus.CREDIT
                    )
                    logger.info(
                        f"Venta {sale.folio} regresada a CRÉDITO "
                        f"(saldo: {sale_balance})"
                    )


# -------------------------------------------------------------------------
# HISTORIAL DE COSTOS
# -------------------------------------------------------------------------
class ProductCostHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cost_history')
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    source = models.CharField(
        max_length=20, 
        choices=[('PURCHASE', 'Compra'), ('MANUAL', 'Manual')],
        default='PURCHASE'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-id']
        indexes = [
            models.Index(fields=['product', 'date']),
            models.Index(fields=['date']),
        ]
        verbose_name_plural = "Product cost histories"

    def __str__(self):
        return f"{self.product.name} - ${self.cost} @ {self.date}"


# -------------------------------------------------------------------------
# SIGNALS - Auditoría y logging
# -------------------------------------------------------------------------
@receiver(post_save, sender=PurchaseItem)
def log_purchase_item_change(sender, instance, created, **kwargs):
    """Registra cambios en items de compra"""
    action = "creado" if created else "actualizado"
    logger.info(
        f"PurchaseItem {action}: {instance.product.name} "
        f"x {instance.quantity} en Compra {instance.purchase.folio}"
    )


@receiver(post_save, sender=SaleItem)
def log_sale_item_change(sender, instance, created, **kwargs):
    """Registra cambios en items de venta"""
    action = "creado" if created else "actualizado"
    logger.info(
        f"SaleItem {action}: {instance.product.name} "
        f"x {instance.quantity} en Venta {instance.sale.folio}"
    )


@receiver(post_save, sender=PaymentAllocation)
def log_payment_allocation(sender, instance, created, **kwargs):
    """Registra asignaciones de pago"""
    action = "creada" if created else "actualizada"
    logger.info(
        f"PaymentAllocation {action}: ${instance.amount} "
        f"de Pago {instance.payment.id} a Venta {instance.sale.folio}"
    )


@receiver(post_save, sender=PurchaseItem)
def create_cost_history(sender, instance, created, **kwargs):
    """Crea registro de historial de costo cuando se crea un item de compra"""
    if created and instance.purchase.status == Purchase.Status.COMPLETED:
        ProductCostHistory.objects.create(
            product=instance.product,
            cost=instance.unit_price,
            date=instance.purchase.date,
            source='PURCHASE'
        )
        logger.debug(
            f"Historial de costo creado para {instance.product.name}: "
            f"${instance.unit_price}"
        )