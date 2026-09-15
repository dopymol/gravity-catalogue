from django.db import models

class Brand(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True)
    logo_text = models.CharField(max_length=30, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ["sort_order","name"]
    def __str__(self): return self.name

class Product(models.Model):
    brand = models.ForeignKey(Brand,on_delete=models.PROTECT,related_name="products")
    model = models.CharField(max_length=120)
    variant = models.CharField(max_length=100,blank=True)
    description = models.CharField(max_length=240)
    selling_price = models.DecimalField(max_digits=12,decimal_places=2)
    mrp = models.DecimalField(max_digits=12,decimal_places=2)
    category = models.CharField(max_length=80,default="Phones")
    colours = models.CharField(max_length=220,blank=True)
    specifications = models.JSONField(default=dict,blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["brand__sort_order","selling_price","model"]
        constraints = [models.UniqueConstraint(fields=["brand","model","variant"],name="unique_brand_model_variant")]
    def __str__(self): return f"{self.brand.name} {self.model} {self.variant}".strip()

