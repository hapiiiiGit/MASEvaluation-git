from rest_framework import serializers
from .models import Invoice, InvoiceLine

class InvoiceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLine
        fields = [
            'id',
            'invoice',
            'description',
            'quantity',
            'unit_price',
            'total',
        ]
        read_only_fields = ['id', 'total']

    def create(self, validated_data):
        # total is calculated in model's save()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # total is calculated in model's save()
        return super().update(instance, validated_data)

class InvoiceSerializer(serializers.ModelSerializer):
    lines = InvoiceLineSerializer(many=True)

    class Meta:
        model = Invoice
        fields = [
            'id',
            'number',
            'customer',
            'date',
            'due_date',
            'status',
            'total',
            'created_by',
            'created_at',
            'lines',
        ]
        read_only_fields = ['id', 'total', 'created_by', 'created_at']

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        invoice = Invoice.objects.create(**validated_data)
        for line_data in lines_data:
            InvoiceLine.objects.create(invoice=invoice, **line_data)
        invoice.calculate_total()
        return invoice

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if lines_data is not None:
            # Remove existing lines and add new ones
            instance.lines.all().delete()
            for line_data in lines_data:
                InvoiceLine.objects.create(invoice=instance, **line_data)
            instance.calculate_total()
        return instance