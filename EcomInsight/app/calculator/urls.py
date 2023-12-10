from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SumAllExpences, ItemsViewSet, ImportExportCSV

router = DefaultRouter()
router.register('items', ItemsViewSet, basename='item')

app_name = 'calculator'
urlpatterns = [
    path('calculate/', SumAllExpences.as_view(), name='calculate'), # API for unauthenticated users.
    path('export/products/csv/', ImportExportCSV.as_view(), name='export_csv'), # API for authenticated users.
    path('', include(router.urls))
]
