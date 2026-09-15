from django.contrib import admin
from .models import Brand, Product

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display=("name","sort_order","is_active")
    prepopulated_fields={"slug":("name",)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=("model","variant","brand","selling_price","mrp","stock","is_active","updated_at")
    list_filter=("brand","category","is_active")
    search_fields=("model","variant","description","brand__name")
    list_editable=("selling_price","mrp","stock","is_active")

