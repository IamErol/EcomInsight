from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from .services import Calculator, UserInputHandler
from rest_framework import viewsets, mixins
from .models import ProductInformation, ProductInformationAdditionalFields
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .import_export import CSVExportImport

from drf_spectacular.utils import (extend_schema_view,
                                   extend_schema,
                                   OpenApiParameter,
                                   OpenApiTypes)

from .serializers import (ProductInfoSerializer,
                          ProductInformationAdditionalFieldsSerializer,
                          CreateProductSerializer)

from .api_queries import (get_all_items,
                          get_items_by_name,
                          get_items_by_sku,
                          get_all_items_for_auth_user)


class SumAllExpences(APIView):
    """View to calculate user input."""

    serializer_class = ProductInfoSerializer

    @extend_schema(request=ProductInfoSerializer,
                   responses={200: ProductInfoSerializer})
    def post(self, request):
        """Post request tho handle calculator input from user."""

        serializer = ProductInfoSerializer(data=request.data,
                                           context={'request': request})

        if serializer.is_valid(raise_exception=True):
            kwargs = serializer.validated_data

            lists = UserInputHandler(kwargs).parse_user_input()

            calculate = Calculator(sum_values=lists.sum_values,
                                   percent_values=lists.percent_values,
                                   user_input=kwargs)

            expenses = calculate.get_total_expences()
            recommended_price = calculate.get_recommended_price(expenses)
            net_profit = calculate.get_net_profit(expenses, recommended_price)

            return Response({'expenses': expenses,
                             'recommended_price': recommended_price,
                             'net_profit': net_profit}
                            )


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'name',
                OpenApiTypes.STR,
                description='Name of the product to filter',
            ),
            OpenApiParameter(
                'sku',
                OpenApiTypes.STR,
                description='Sku of the product to filter',
            ),
        ]
    )
)
class ItemsViewSet(viewsets.ModelViewSet, mixins.UpdateModelMixin, ):
    """Perform CRUD operations."""

    queryset = get_all_items()
    serializer_class = ProductInfoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self, *args, **kwargs):
        """Get serializer class."""

        if self.action == 'create':
            return CreateProductSerializer
        return ProductInfoSerializer

    def get_queryset(self):
        """Get queryset."""

        user = self.request.user.pk
        queryset = get_all_items_for_auth_user(user)
        name = self.request.query_params.get('name')
        sku = self.request.query_params.get('sku')

        if name:
            queryset = get_items_by_name(name)
        if sku:
            queryset = get_items_by_sku(sku)
        return queryset


class OtherFields(mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """View to list, update and delete other fields."""

    serializer_class = ProductInformationAdditionalFieldsSerializer
    queryset = ProductInformationAdditionalFields.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class ImportExportCSV(APIView):
    """Class for operations related to CSV files."""

    serializer_class = ProductInfoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get file with products of user in CSV format."""

        user = self.request.user.pk
        data = get_all_items_for_auth_user(user)

        write_to_csv = CSVExportImport(data)
        csv_file = write_to_csv.export_to_csv(queryset=data,
                                              file_name='products')
        return csv_file
