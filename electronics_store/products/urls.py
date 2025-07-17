from django.urls import path
from products import views


app_name = 'products'

urlpatterns = [
    path('<slug:category_slug>/', views.CatalogView.as_view(), name='index'),
    path('product/<slug:product_slug>/', views.ProductView.as_view(), name='product')
]
