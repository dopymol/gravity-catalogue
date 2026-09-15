from django.test import TestCase
from django.urls import reverse
from .models import Brand,Product
class CatalogueTests(TestCase):
    def setUp(self):
        brand=Brand.objects.create(name="Test",slug="test")
        Product.objects.create(brand=brand,model="X1",variant="8/128",description="Test phone",selling_price=100,mrp=120)
    def test_page_and_htmx_results(self):
        self.assertContains(self.client.get(reverse("index")),"X1")
        self.assertContains(self.client.get(reverse("product_results"),{"q":"X1"}),"Test phone")
    def test_pwa_routes(self):
        self.assertEqual(self.client.get(reverse("manifest")).status_code,200)
        self.assertContains(self.client.get(reverse("service_worker")),"gravity-v1")
    def test_product_modal_and_whatsapp(self):
        product=Product.objects.get(model="X1")
        response=self.client.get(reverse("product_detail",args=[product.pk]))
        self.assertContains(response,"Share on WhatsApp")
        self.assertContains(response,"wa.me")
        self.assertContains(response,"Product specifications")
    def test_excel_export(self):
        response=self.client.get(reverse("export_excel"))
        self.assertEqual(response.status_code,200)
        self.assertIn("spreadsheetml",response["Content-Type"])
