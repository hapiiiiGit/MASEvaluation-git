from django.db import models
from django.conf import settings
from purchases.models import Supplier

class InventoryItem(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    reorder_level = models.PositiveIntegerField(default=0)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_items'
    )

    def __str__(self):
        return f"{self.sku} - {self.name}"

    def is_below_reorder(self):
        return self.quantity <= self.reorder_level

class InventoryAdjustment(models.Model):
    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name='adjustments'
    )
    date = models.DateField(auto_now_add=True)
    quantity_change = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='inventory_adjustments'
    )

    def __str__(self):
        return f"Adjustment {self.id} for {self.item.sku} on {self.date}: {self.quantity_change}"