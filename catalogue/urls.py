from django.urls import path
from . import views
urlpatterns=[
    path("",views.index,name="index"),
    path("products/",views.product_results,name="product_results"),
    path("products/<int:pk>/",views.product_detail,name="product_detail"),
    path("export/",views.export_excel,name="export_excel"),
    path("manifest.json",views.manifest,name="manifest"),
    path("service-worker.js",views.service_worker,name="service_worker"),
]
