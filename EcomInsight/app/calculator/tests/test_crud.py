from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from django.urls import reverse
from calculator.models import ProductInformation, ProductInformationAdditionalFields
from calculator.serializers import ProductInfoSerializer, ProductInformationAdditionalFieldsSerializer
from decimal import Decimal
import json

URL_ITEM = reverse('calculator:item-list')
URL_POST = reverse('calculator:calculate')


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


def detail_url(_id):
    """Create and return detail url for other fields object."""
    return reverse('calculator:item-detail', args=[str(_id)])


class ProductInformationTest(TestCase):
    """Test ProductInformation crud."""

    def setUp(self) -> None:
        self.user = create_user(
            email='test@example.com',
            password='testpass1234')
        self.client = APIClient()

    def test_unauthorized_user(self):
        """Test user is not authenticated."""
        res = self.client.get(URL_ITEM)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_create(self):
        """Test unauthorized user save product to db."""
        product = create_product_input()
        res = self.client.post(URL_ITEM, **product)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized_user_calculate(self):
        """Test unauthorized user can use calculator functionality without save functionality."""
        product = create_product_input()
        res = self.client.post(URL_POST, product)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertContains(res, 'recommended_price')
        self.assertNotEqual(res.data['expenses'], 0)
        self.assertNotContains(res, 'name')

    def test_unauthenticated_patch_other_fields(self):
        """Test patch request for unauthenticated user."""
        create_product_input(user=self.user)
        created_product = ProductInformation.objects.get(name='Test')
        other_field = ProductInformationAdditionalFields.objects.get(product=created_product)

        _id = other_field.id
        payload = {'field_name': 'updated marketing',
                   'value': 200, 'id': _id}

        res = self.client.patch(detail_url(_id), payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorised_get_products(self):
        """Test get request for unauthorised user."""
        product = create_product_input()
        res = self.client.get(URL_ITEM)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_products(self):
        """Test get request for products."""
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        create_product_input(user=self.user)
        create_product_input(user=self.user)

        product_object = ProductInformation.objects.all()
        serializer = ProductInfoSerializer(product_object, many=True)
        res = self.client.get(URL_ITEM)
        self.assertEqual(res.data, serializer.data)


class ProductInformationAuthenticatedUserTest(TestCase):
    """Test CRUD operations for ProductInformation by authenticated user."""

    def setUp(self):
        self.user = create_user(email='authenticated@example.com', password='testpass1234')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_product(self):
        """Test creating a product as an authenticated user."""
        product = create_product_input()
        response = self.client.post(URL_ITEM, product)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], product['name'])
        self.assertIn('other_fields', response.data)

    def test_read_product(self):
        """Test reading a product's details as an authenticated user."""
        product = create_product_input(user=self.user)
        response = self.client.get(detail_url(product.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], product.name)

    def test_update_product(self):
        """Test updating a product as an authenticated user."""
        product = create_product_input(user=self.user)
        payload = {'name': 'Updated Name', 'sku': 'Updated-123'}
        response = self.client.patch(detail_url(product.id), payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product.refresh_from_db()
        self.assertEqual(product.name, 'Updated Name')

    def test_delete_product(self):
        """Test deleting a product as an authenticated user."""
        product = create_product_input(user=self.user)
        response = self.client.delete(detail_url(product.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProductInformation.objects.filter(id=product.id).exists())

    def test_list_products(self):
        """Test listing all products as an authenticated user."""
        create_product_input(user=self.user)
        create_product_input(user=self.user, name='Second Product')
        response = self.client.get(URL_ITEM)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_products_by_name(self):
        """Test filtering products by name as an authenticated user."""
        create_product_input(user=self.user)
        create_product_input(user=self.user, name='Second Product')
        response = self.client.get(URL_ITEM, {'name': 'Second Product'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Second Product')

    def test_filter_products_by_sku(self):
        """Test filtering products by sku as an authenticated user."""
        create_product_input(user=self.user)
        create_product_input(user=self.user, sku='Second Product')
        response = self.client.get(URL_ITEM, {'sku': 'Second Product'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['sku'], 'Second Product')

    def test_add_other_fields(self):
        """Test post request for other fields."""
        product = create_product_input(user=self.user)
        _id = product.id
        new_field_name = "new"
        new_value = 525

        payload = {
            "other_fields": [{
                "field_name": new_field_name,
                "value": new_value,
            }],
        }

        response = self.client.patch(detail_url(_id), json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        product.refresh_from_db()

        # Check if the new other_fields have been added
        new_field_exists = ProductInformationAdditionalFields.objects.filter(
            product=product,
            field_name=new_field_name,
            value=Decimal(new_value)
        ).exists()

        self.assertTrue(new_field_exists, "New other field was not added.")

    def test_patch_other_fields(self):
        """Test patch request for other fields."""
        product = create_product_input(user=self.user)
        other_field = ProductInformationAdditionalFields.objects.get(product=product)
        _id = product.id
        payload = {
            "other_fields":
                [{
                    "field_name": "updated",
                    "value": 5000,
                    "id": other_field.id}
                ],
            "name": "Updated Test",
            "sku": "Updated-123",
        }

        response = self.client.patch(detail_url(_id), json.dumps(payload), content_type='application/json')
        product.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(product.other_fields.get().field_name, 'updated')
        self.assertEqual(product.other_fields.get().value, 5000)
        self.assertEqual(product.name, 'Updated Test')
        self.assertEqual(product.sku, 'Updated-123')

    def test_put_other_fields(self):
        """Test put request for other fields."""
        product = create_product_input(user=self.user)
        other_field = ProductInformationAdditionalFields.objects.get(product=product)
        _id = product.id
        payload = {
            "other_fields":
                [{
                    "field_name": "updated",
                    "value": 5000,
                    "id": other_field.id}
                ],
            "name": "Updated Test",
            "sku": "Updated-123",
        }

        response = self.client.put(detail_url(_id), json.dumps(payload), content_type='application/json')
        product.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(product.other_fields.get().field_name, 'updated')
        self.assertEqual(product.other_fields.get().value, 5000)
        self.assertEqual(product.name, 'Updated Test')
        self.assertEqual(product.sku, 'Updated-123')

    def test_delete_other_fields(self):
        """Test delete request for other fields."""
        product = create_product_input(user=self.user)
        other_field = ProductInformationAdditionalFields.objects.get(product=product)
        _id = product.id
        response = self.client.delete(detail_url(_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProductInformation.objects.filter(id=product.id).exists())
