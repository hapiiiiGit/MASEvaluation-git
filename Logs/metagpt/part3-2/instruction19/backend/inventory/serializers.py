from rest_framework import serializers
from .models import InventoryItem, InventoryAdjustment
from purchases.models import Supplier

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_info']

class InventoryItemSerializer(serializers.ModelSerializer):
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(), source='supplier', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = InventoryItem
        fields = [
            'id',
            'sku',
            'name',
            'quantity',
            'unit_cost',
            'reorder_level',
            'supplier',
            'supplier_id',
        ]
        read_only_fields = ['id', 'quantity', 'supplier']

class InventoryAdjustmentSerializer(serializers.ModelSerializer):
    item = InventoryItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=InventoryItem.objects.all(), source='item', write_only=True
    )
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = InventoryAdjustment
        fields = [
            'id',
            'item',
            'item_id',
            'date',
            'quantity_change',
            'reason',
            'created_by',
        ]
        read_only_fields = ['id', 'date', 'created_by', 'item']

    def create(self, validated_data):
        return InventoryAdjustment.objects.create(**validated_data)