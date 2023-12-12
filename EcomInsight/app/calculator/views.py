import os
from celery.result import AsyncResult
from django.core.cache import cache
from rest_framework import status
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .services import Calculator, UserInputHandler
from rest_framework import viewsets, mixins
from .models import ProductInformationAdditionalFields
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (extend_schema_view,
                                   extend_schema,
                                   OpenApiParameter,
                                   OpenApiTypes)
from .serializers import (ProductInfoSerializer,
                          ProductInformationAdditionalFieldsSerializer,
                          CreateProductSerializer, CsvSerializer)
from .api_queries import (get_all_items,
                          get_items_by_name,
                          get_items_by_sku,
                          get_all_items_for_auth_user)
from .tasks import generate_csv_task


class SumAllExpences(APIView):
    """
    View to calculate user input.
    This view provides unauthorized users access to calculation functionality.
    It returns expenses, recommended price and net profit, saving is not allowed.
    """

    serializer_class = ProductInfoSerializer

    @extend_schema(request=ProductInfoSerializer,
                   responses={200: ProductInfoSerializer})
    def post(self, request):
        """Post request to handle calculator input from user."""

        serializer = ProductInfoSerializer(data=request.data,
                                           context={'request': request})

        if serializer.is_valid(raise_exception=True):
            kwargs = serializer.validated_data

            # Parse user input data and prepare for further calculations.
            lists = UserInputHandler(kwargs).parse_user_input()
            # Calculate expenses, recommended price and net profit.
            calculate = Calculator(sum_values=lists.sum_values,
                                   percent_values=lists.percent_values,
                                   user_input=kwargs)

            expenses = calculate.get_total_expenses()
            recommended_price = calculate.get_recommended_price(expenses)
            net_profit = calculate.get_net_profit(expenses, recommended_price)

            return Response({'expenses': expenses,
                             'recommended_price': recommended_price,
                             'net_profit': net_profit})


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
    """Perform CRUD operations for items."""

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
        name = self.request.query_params.get('name')
        sku = self.request.query_params.get('sku')

        cache_key = 'Items'
        cached_queryset = cache.get(cache_key)


        queryset = get_all_items_for_auth_user(user)

        if name:
            return get_items_by_name(name)
        if sku:
            return get_items_by_sku(sku)
        if cached_queryset is not None:
            return cached_queryset

        cache.set(cache_key, queryset, timeout=60 * 5)
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
    """
    Class for operations related to CSV files.
    Post method creates a celery task to generate a CSV file and returns the task ID.
    Get method checks the status of a CSV generation task and returns the file if ready.
    """

    serializer_class = ProductInfoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CsvSerializer
        return ProductInfoSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='task_id', description='Task ID for the CSV generation', required=True, type=str)
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        GET method to handle CSV download requests.
        This method checks the status of a CSV generation task and returns the file if ready.
        """
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({'error': 'No task_id provided'}, status=400)
        # Getting task result.
        task_result = AsyncResult(task_id)

        if task_result.state == 'SUCCESS':
            file_path = task_result.get()
            with open(file_path, 'rb') as f:
                response = HttpResponse(f, content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="products.csv"'
            os.remove(file_path)  # Remove file after download to save space.
            return response
        else:
            return Response({'status': 'Processing'}, status=status.HTTP_102_PROCESSING)

    def post(self, request):
        """
        POST method to start CSV generation.
        This method triggers a Celery task to generate a CSV file.
        """
        user_id = request.user.id
        task = generate_csv_task.delay(user_id)
        return Response({'task_id': task.id}, status=status.HTTP_200_OK)
