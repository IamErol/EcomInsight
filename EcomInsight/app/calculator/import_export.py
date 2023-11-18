import csv
from django.http import HttpResponse


class CSVExportImport:
    """Class for exporting and importing CSV files."""
    def __init__(self, model_class, exceptions=None):
        self.model_class = model_class
        self.exceptions = exceptions

    def get_model_fields(self):
        """
        Get the fields of the Django model class, excluding exceptions.

        Yields:
            str: The name of each field in the model.
        """
        # queryset.model._meta.get_fields()
        for field in self.model_class.model._meta.get_fields():
            if self.exceptions is None or field.name not in self.exceptions:
                yield field.name

    def export_to_csv(self, queryset, file_name: str):
        """Generate and export a CSV file from a queryset of the given model."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_name}.csv"'

        writer = csv.writer(response)

        # Write column headers dynamically based on the model's fields
        headers = [field for field in self.get_model_fields()]
        writer.writerow(headers)

        # Write data from the queryset to the CSV file
        for item in queryset:
            row = [getattr(item, field) for field in headers]
            writer.writerow(row)

        return response
