from django.contrib import admin

from products.models import Brands, Products, Categories, Characteristics, ProductImage


@admin.register(Brands)
class BrandsAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name']


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name']


class CharacteristicsInline(admin.TabularInline):
    model = Characteristics


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 5


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ['name', 'brand', 'quantity', 'price', 'discount', 'sell_price']
    list_editable = ['discount']
    search_fields = ['name', 'description']
    list_filter = ['discount', 'category', 'brand']
    fields = ['name', 'category', 'brand', 'slug', 'image', 'description', ('price', 'discount'), 'quantity']
    inlines = [CharacteristicsInline, ProductImageInline]






