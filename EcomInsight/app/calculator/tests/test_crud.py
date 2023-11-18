from pprint import pprint

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import force_authenticate
from django.test import TestCase
from django.urls import reverse
from django.shortcuts import get_object_or_404

from calculator.models import ProductInformation, ProductInformationAdditionalFields
from calculator.serializers import ProductInfoSerializer, ProductInformationAdditionalFieldsSerializer

URL_GET = reverse('calculator:item-list')
URL_OTHER_FIELDS = URL_GET
URL_POST = reverse('calculator:calculate')


# class ProductInformationSerializerTest(TestCase):
def create_user(email='example@example.com', password='test1234'):
    return get_user_model().objects.create(email=email, password=password)


def create_product_input(user=None, **params):
    """Create test product input."""

    defaults = {
        "other_fields":
            {
                "field_name": "marketing",
                "value": 100
            }
        ,
        "name": "Test",
        "sku": "Test-123",
        "quantity": 500,
        "margin_percent": 25,
        "buying_price": 50,
        "transportation": 5,
        "packaging": 10,
        "warehouse": 20,
        "marketplace_commission_percent": 6,
        "recommended_price": 0,
        "expenses": 0,
        "net_profit": 0
    }
    defaults.update(params)
    other_fields_data = defaults.pop("other_fields", None)

    if user:
        defaults["product_owner"] = user
        product = ProductInformation.objects.create(**defaults)
        other_fields_data['product_id'] = product.id
        other_fields = ProductInformationAdditionalFields.objects.create(**other_fields_data)
        product.other_fields.add(other_fields)
        return product
    return defaults


def detail_url(id):
    """Create and return detail url for other fields object."""
    return reverse('calculator:other_fields-detail', args=[str(id)])


class ProductInformationSerializerTest(TestCase):
    """Test product serializer."""

    def setUp(self) -> None:
        self.user = create_user(
            email='test@example.com',
            password='testpass1234')
        self.client = APIClient()

    def test_unauthorized_user(self):
        """Test user is not authenticated."""
        res = self.client.get(URL_GET)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_create(self):
        """Test unauthorized user save product to db."""
        product = create_product_input()
        res = self.client.post(URL_GET, **product)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_calculate(self):
        """Test unauthorized user can use calculator functionality without save functionality."""
        product = create_product_input()
        res = self.client.post(URL_POST, product)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, 'recommended_price')
        self.assertNotEqual(res.data['expenses'], 0)
        self.assertNotContains(res, 'name')

    def test_patch_other_fields(self):
        """Test patch request for other fields."""
        self.user = create_user(
            email='test1@example.com',
            password='testpass1234',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        create_product_input(user=self.user)
        created_product = ProductInformation.objects.get(name='Test')
        other_field = ProductInformationAdditionalFields.objects.get(product=created_product)
        _id = other_field.id
        payload = {'field_name': 'updated marketing',
                   'value': 200, 'id': _id}

        URL_OTHER_FIELDS = detail_url(_id)
        res = self.client.patch(URL_OTHER_FIELDS, payload)
        other_field = ProductInformationAdditionalFields.objects.get(product=created_product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(other_field.field_name, 'updated marketing')
        self.assertEqual(other_field.value, 200)

    def test_unauthenticated_patch_other_fields(self):
        """Test patch request for unauthenticated user."""
        create_product_input(user=self.user)
        created_product = ProductInformation.objects.get(name='Test')
        other_field = ProductInformationAdditionalFields.objects.get(product=created_product)

        id = other_field.id
        payload = {'field_name': 'updated marketing',
                   'value': 200, 'id': id}

        URL_OTHER_FIELDS = detail_url(id)
        res = self.client.patch(URL_OTHER_FIELDS, payload)
        other_field = ProductInformationAdditionalFields.objects.get(product=created_product)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorised_get_products(self):
        """Test get request for unauthorised user."""
        product = create_product_input()
        res = self.client.get(URL_GET)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_products(self):
        """Test get request for products."""
        user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        create_product_input(user=self.user)
        create_product_input(user=self.user)

        product_object = ProductInformation.objects.all()
        serializer = ProductInfoSerializer(product_object, many=True)
        res = self.client.get(URL_GET)
        self.assertEqual(res.data, serializer.data)
