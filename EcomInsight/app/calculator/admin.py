from django.contrib import admin
from .models import ProductInformation, ProductInformationAdditionalFields
# Register your models here.
admin.site.register(ProductInformation)
admin.site.register(ProductInformationAdditionalFields)