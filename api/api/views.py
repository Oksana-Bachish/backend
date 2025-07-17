from rest_framework import viewsets
from .models import Products
from api.serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer

