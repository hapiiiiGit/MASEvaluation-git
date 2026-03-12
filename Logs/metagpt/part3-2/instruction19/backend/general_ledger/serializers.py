from rest_framework import serializers
from .models import Account, JournalEntry, JournalEntryLine

class AccountSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Account
        fields = ['id', 'name', 'code', 'type', 'parent']

class JournalEntryLineSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)
    account_id = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(), source='account', write_only=True
    )

    class Meta:
        model = JournalEntryLine
        fields = ['id', 'journal_entry', 'account', 'account_id', 'debit', 'credit']

class JournalEntrySerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)
    lines = JournalEntryLineSerializer(many=True)

    class Meta:
        model = JournalEntry
        fields = ['id', 'date', 'description', 'created_by', 'created_at', 'lines']

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        journal_entry = JournalEntry.objects.create(**validated_data)
        for line_data in lines_data:
            account = line_data.pop('account')
            JournalEntryLine.objects.create(journal_entry=journal_entry, account=account, **line_data)
        return journal_entry

    def update(self, instance, validated_data):
        lines_data = validated_data.pop('lines', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if lines_data is not None:
            # Remove existing lines and add new ones
            instance.lines.all().delete()
            for line_data in lines_data:
                account = line_data.pop('account')
                JournalEntryLine.objects.create(journal_entry=instance, account=account, **line_data)
        return instance