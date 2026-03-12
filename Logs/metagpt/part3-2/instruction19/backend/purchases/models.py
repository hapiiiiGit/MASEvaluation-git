from django.db import models
from django.conf import settings
from decimal import Decimal

# Import InventoryItem from inventory app for FK relation
from inventory.models import InventoryItem

class Supplier(models.Model):
    name = models.CharField(max_length=255, unique=True)
    contact_info = models.TextField(blank=True)

    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ORDERED', 'Ordered'),
        ('RECEIVED', 'Received'),
        ('CANCELLED', 'Cancelled'),
    ]

    number = models.CharField(max_length=30, unique=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders'
    )
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='purchase_orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PO {self.number} - {self.supplier.name}"

    def calculate_total(self):
        total = sum(line.total for line in self.lines.all())
        self.total = total
        self.save(update_fields=['total'])
        return total

class PurchaseOrderLine(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.PROTECT,
        related_name='purchase_order_lines'
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    def save(self, *args, **kwargs):
        self.total = Decimal(self.quantity) * self.unit_price
        super().save(*args, **kwargs)
        # Update purchase order total after saving line
        if self.purchase_order:
            self.purchase_order.calculate_total()

    def __str__(self):
        return f"{self.item.name} x {self.quantity} @ {self.unit_price}"