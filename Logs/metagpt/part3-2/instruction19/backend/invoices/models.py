from django.db import models
from django.conf import settings
from decimal import Decimal

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
        ('CANCELLED', 'Cancelled'),
    ]

    number = models.CharField(max_length=30, unique=True)
    customer = models.CharField(max_length=255)
    date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='invoices'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.number} - {self.customer}"

    def calculate_total(self):
        total = sum(line.total for line in self.lines.all())
        self.total = total
        self.save(update_fields=['total'])
        return total

class InvoiceLine(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))

    def save(self, *args, **kwargs):
        self.total = Decimal(self.quantity) * self.unit_price
        super().save(*args, **kwargs)
        # Update invoice total after saving line
        if self.invoice:
            self.invoice.calculate_total()

    def __str__(self):
        return f"{self.description} x {self.quantity} @ {self.unit_price}"