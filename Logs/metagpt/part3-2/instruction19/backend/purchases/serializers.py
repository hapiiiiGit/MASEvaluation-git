from rest_framework import serializers
from .models import Supplier, PurchaseOrder, PurchaseOrderLine
from inventory.models import InventoryItem

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id',
            'name',
            'contact_info',
        ]

class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(
        queryset=InventoryItem.objects.all()
    )
    item_detail = serializers.StringRelatedField(source='item', read_only=True)

    class Meta:
        model = PurchaseOrderLine
        fields = [
            'id',
            'purchase_order',
            'item',
            'item_detail',
            'quantity',
            'unit_price',
            'total',
        ]
        read_only_fields = ['id', 'total', 'item_detail']

class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(), source='supplier', write_only=True
    )
    lines = PurchaseOrderLineSerializer(many=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id',
            'number',
            'supplier',
            'supplier_id',
            'date',
            'status',
            'total',
            'created_by',
            'created_at',
            'lines',
        ]
        read_only_fields = ['id', 'total', 'created_by', 'created_at', 'supplier']

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        supplier = validated_data.pop('supplier')
        purchase_order = PurchaseOrder.objects.create(supplier=supplier, **validated_data)
        for line_data in lines_data:
            PurchaseOrderLine.objects.create(purchase_order=purchase_order, **line_data)
        purchase_order.calculate_total()
        return purchase_order

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)
        supplier = validated_data.pop('supplier', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if supplier is not None:
            instance.supplier = supplier
        instance.save()

        if lines_data is not None:
            # Remove existing lines and add new ones
            instance.lines.all().delete()
            for line_data in lines_data:
                PurchaseOrderLine.objects.create(purchase_order=instance, **line_data)
            instance.calculate_total()
        return instance