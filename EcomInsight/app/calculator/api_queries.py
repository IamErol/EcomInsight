from .models import ProductInformation


def get_all_items():
    """Get all records from database."""
    return (ProductInformation.objects.
            prefetch_related('other_fields').
            all())


def get_items_by_name(name: str):
    """Filter result by name."""
    return (ProductInformation.objects.
            select_related('product_owner').
            filter(name__icontains=name))


def get_items_by_sku(sku: str):
    """Filter result by sku."""
    return (ProductInformation.objects.
            select_related('product_owner').
            filter(sku=sku))


def get_all_items_for_auth_user(user: int):
    """Get all times for authenticated user."""
    return (ProductInformation.objects.
            filter(product_owner=user).
            prefetch_related('other_fields').all())
