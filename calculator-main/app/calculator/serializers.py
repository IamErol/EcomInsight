"""Calculator app serializers."""

from rest_framework import serializers, status
from .models import ProductInformation, ProductInformationAdditionalFields
from rest_framework.fields import CurrentUserDefault
from django.db import transaction
from .services import UserInputHandler, Calculator


class ProductInformationAdditionalFieldsSerializer(serializers.ModelSerializer):
    """ProductInfo model serializer."""

    id = serializers.IntegerField(required=False)

    class Meta:
        """Metaclass options."""

        model = ProductInformationAdditionalFields

        fields = ['id',
                  'field_name',
                  'value',
                  'product']

        read_only_fields = ['product']


class ProductInfoSerializer(serializers.ModelSerializer):
    """ProductInfo model serializer."""

    other_fields = ProductInformationAdditionalFieldsSerializer(many=True, required=False)

    class Meta:
        """Metaclass options."""

        model = ProductInformation

        exclude = ['created_at',
                   'product_owner']

        extra_kwargs = {'recommended_price': {'allow_null': True},
                        'expenses': {'allow_null': True},
                        'net_profit': {'allow_null': True},
                        }

    def create_other_fields(self, fields, product):
        """Create other fields helper function for product."""

        for field in fields:
            field_name = field['field_name']
            value = field['value']
            field_obj = ProductInformationAdditionalFields.objects.create(
                product=product,
                field_name=field_name,
                value=value
            )
            product.other_fields.add(field_obj)

    def create(self, validated_data):
        """Create product information."""

        user = self.context['request'].user

        if user.is_authenticated:
            other_fields = validated_data.pop('other_fields', [])
            product_information = ProductInformation.objects.create(product_owner=user, **validated_data)

            self.create_other_fields(other_fields, product_information)
            product_information.save()
            return product_information

        raise serializers.ValidationError('Unauthorized user.')

    def update(self, instance, validated_data):
        """Update product information."""

        other_fields_data = validated_data.pop('other_fields', [])

        # Extract the field ids and create a mapping of id to field_data
        field_data_mapping = {field_data.get('id'): field_data for field_data in other_fields_data if
                              field_data.get('id')}

        # Fetch all existing fields related to the instance with prefetch_related
        existing_fields = instance.other_fields.all()

        lists = UserInputHandler(validated_data).parse_user_input()
        sum_list, percent_list = lists.sum_values, lists.percent_values
        calculate = Calculator(sum_values=sum_list,
                               percent_values=percent_list,
                               user_input=validated_data)

        expenses = calculate.get_total_expences()
        recommended_price = calculate.get_recommended_price(expenses)
        net_profit = calculate.get_net_profit(expenses, recommended_price)

        with transaction.atomic():
            # Update existing fields using bulk update
            for field_instance in existing_fields:
                field_data = field_data_mapping.get(field_instance.id)
                if field_data:
                    field_instance.field_name = field_data.get('field_name', field_instance.field_name)
                    field_instance.value = field_data.get('value', field_instance.value)

            validated_data['recommended_price'] = recommended_price
            validated_data['expenses'] = expenses
            validated_data['net_profit'] = net_profit
            # print(f"validated data : {validated_data}")
            # insta.expenses = expenses

            # Extract the fields that need to be updated
            # fields_to_update = [
            #     ProductInformationAdditionalFields(
            #         id=field_id,
            #         field_name=field_data.get('field_name'),
            #         value=field_data.get('value'),
            #         product=instance
            #     )
            #     for field_id, field_data in field_data_mapping.items()
            #     if field_id and 'id' not in field_data
            # ]

            # Perform bulk update for existing fields
            ProductInformationAdditionalFields.objects.bulk_update(existing_fields, ['field_name', 'value'])

            # Create new fields
            new_fields = [
                ProductInformationAdditionalFields(
                    product=instance,
                    field_name=field_data.get('field_name'),
                    value=field_data.get('value')
                )
                for field_data in other_fields_data if 'id' not in field_data
            ]

            # Bulk create new fields
            ProductInformationAdditionalFields.objects.bulk_create(new_fields)

        return super().update(instance, validated_data)


class CreateProductInformationAdditionalFieldsSerializer(serializers.ModelSerializer):
    """ProductInfo model serializer."""

    class Meta:
        model = ProductInformationAdditionalFields
        fields = ['id',
                  'field_name',
                  'value',
                  'product']

        read_only_fields = ['product',
                            'id']


class CreateProductSerializer(ProductInfoSerializer):
    """ProductInfo model serializer."""

    other_fields = CreateProductInformationAdditionalFieldsSerializer(many=True,
                                                                      required=False)

    class Meta:
        """Metaclass options."""

        model = ProductInformation

        exclude = ['created_at',
                   'product_owner',
                   'id',
                   'recommended_price',
                   'expenses',
                   'net_profit']

        extra_kwargs = {'id': {'read_only': True}}
