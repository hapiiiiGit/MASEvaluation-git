from django.db import models
from django.utils import timezone
from django.core.files.base import ContentFile
import csv
import io
import json

class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('donation', 'Donation'),
        ('activity', 'Donor Activity'),
        ('inventory', 'Inventory'),
        ('custom', 'Custom'),
    ]

    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=32, choices=REPORT_TYPE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    params = models.JSONField(default=dict, blank=True)
    data = models.JSONField(default=dict, blank=True)

    def generate(self, params: dict):
        """
        Generate report data based on type and params.
        This method should be called to populate the 'data' field.
        """
        # Example: For demonstration, just echo params as data.
        # In production, this should query the database and aggregate data.
        self.params = params
        if self.type == 'donation':
            # Example: Aggregate donation data
            self.data = {
                "summary": "Donation report generated.",
                "params": params
            }
        elif self.type == 'activity':
            self.data = {
                "summary": "Donor activity report generated.",
                "params": params
            }
        elif self.type == 'inventory':
            self.data = {
                "summary": "Inventory report generated.",
                "params": params
            }
        else:
            self.data = {
                "summary": "Custom report generated.",
                "params": params
            }
        self.save()
        return self

    def export(self, format: str):
        """
        Export the report data in the specified format.
        Supported formats: 'csv', 'json'
        Returns a Django File object.
        """
        if format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            # Flatten JSON data for CSV export
            if isinstance(self.data, dict):
                for key, value in self.data.items():
                    writer.writerow([key, value])
            else:
                writer.writerow([str(self.data)])
            content = output.getvalue()
            output.close()
            filename = f'report_{self.id}.csv'
            return ContentFile(content, name=filename)
        elif format == 'json':
            content = json.dumps(self.data, indent=2)
            filename = f'report_{self.id}.json'
            return ContentFile(content, name=filename)
        else:
            raise ValueError("Unsupported export format: {}".format(format))

    def __str__(self):
        return f"Report {self.id} ({self.get_type_display()}) - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"