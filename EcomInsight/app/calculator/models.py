from django.db import models
from django.conf import settings


class ProductInformation(models.Model):
    """
    Product model that contains all information about product.
    """
    name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sku = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    margin_percent = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    product_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    buying_price = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    transportation = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    packaging = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    warehouse = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    marketplace_commission_percent = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    recommended_price = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    expenses = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    net_profit = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name_plural = 'ProductInformation'


class ProductInformationAdditionalFields(models.Model):
    """Table for additional fields that user might add for its products."""

    field_name = models.CharField(max_length=255, null=True, blank=True)
    value = models.DecimalField(max_digits=9, decimal_places=4, null=True, blank=True)
    product = models.ForeignKey(ProductInformation,
                                related_name='other_fields',
                                on_delete=models.CASCADE)

    def __str__(self):
        return str(self.field_name)

    class Meta:
        verbose_name_plural = 'ProductInformationAdditionalFields'
