import csv
from .api_queries import get_all_items_for_auth_user
from .models import ProductInformation


def write_to_csv(user, file_path):
    """
    Write authorised user's products to CSV file.
    """
    # Fetch products and prefetch related fields
    products = get_all_items_for_auth_user(user)
    additional_field_names = set()
    for product in products:
        for field in product.other_fields.all():
            additional_field_names.add(field.field_name)

    # Prepare file path for CSV
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write CSV headers
        field_names = [field.name for field in ProductInformation._meta.get_fields() if field.name != 'other_fields']
        writer.writerow(field_names + list(additional_field_names))

        # Write data rows
        for product in products:
            row_data = [getattr(product, field) for field in field_names]

            # Dynamically add additional field data
            additional_data = {field.field_name: field.value for field in product.other_fields.all()}
            for field_name in additional_field_names:
                row_data.append(additional_data.get(field_name, ''))

            writer.writerow(row_data)

# TODO: Change the order of the fields in the CSV file.
