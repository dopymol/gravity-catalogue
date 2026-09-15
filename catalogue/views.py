from io import BytesIO
from urllib.parse import quote
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from openpyxl import Workbook
from .models import Brand, Product

def _context(request):
    query=request.GET.get("q","").strip()
    brand_slug=request.GET.get("brand","").strip()
    products=Product.objects.filter(is_active=True,brand__is_active=True).select_related("brand")
    if query:
        products=products.filter(Q(model__icontains=query)|Q(variant__icontains=query)|Q(description__icontains=query)|Q(brand__name__icontains=query))
    if brand_slug: products=products.filter(brand__slug=brand_slug)
    brands=Brand.objects.filter(is_active=True).annotate(product_count=Count("products",filter=Q(products__is_active=True)))
    latest=Product.objects.filter(is_active=True).order_by("-updated_at").values_list("updated_at",flat=True).first()
    return {"products":products,"brands":brands,"query":query,"selected_brand":brand_slug,"total_products":Product.objects.filter(is_active=True,brand__is_active=True).count(),"last_updated":latest or timezone.now()}

def index(request):
    return render(request,"catalogue/index.html",_context(request))

def product_results(request):
    return render(request,"catalogue/partials/catalogue_content.html",_context(request))

def product_detail(request, pk):
    product=get_object_or_404(Product.objects.select_related("brand"),pk=pk,is_active=True)
    specs="\n".join(f"- {key}: {value}" for key,value in product.specifications.items())
    message=(f"*{product.brand.name} {product.model} {product.variant}*\n"
             f"{product.description}\n\nSelling price: ₹{product.selling_price:,.0f}\n"
             f"MRP: ₹{product.mrp:,.0f}\n"
             f"{('Colours: '+product.colours) if product.colours else ''}\n\nSpecifications:\n{specs}\n\n"
             f"View product: {request.build_absolute_uri()}")
    return render(request,"catalogue/detail.html",{
        "product":product,
        "savings":product.mrp-product.selling_price,
        "whatsapp_url":"https://wa.me/?text="+quote(message),
    })

def export_excel(request):
    context=_context(request)
    workbook=Workbook(); sheet=workbook.active; sheet.title="Price List"
    sheet.append(["Brand","Model","Variant","Description","Selling Price","MRP","Category","Colours","Stock"])
    for p in context["products"]:
        sheet.append([p.brand.name,p.model,p.variant,p.description,float(p.selling_price),float(p.mrp),p.category,p.colours,p.stock])
    stream=BytesIO(); workbook.save(stream)
    response=HttpResponse(stream.getvalue(),content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"]='attachment; filename="gravity-price-list.xlsx"'
    return response

def manifest(request):
    return JsonResponse({"name":"Gravity Price List","short_name":"Gravity","start_url":"/","scope":"/","display":"standalone","background_color":"#ffffff","theme_color":"#ffffff","description":"Mobile retailer product price list","icons":[{"src":"/static/icons/icon.svg","sizes":"any","type":"image/svg+xml","purpose":"any maskable"}]})

def service_worker(request):
    source='''const CACHE="gravity-v1";const ASSETS=["/","/static/css/app.css","/static/js/app.js","/static/icons/icon.svg"];self.addEventListener("install",e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS))));self.addEventListener("activate",e=>e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))))));self.addEventListener("fetch",e=>{if(e.request.method!=="GET")return;e.respondWith(fetch(e.request).then(r=>{const copy=r.clone();caches.open(CACHE).then(c=>c.put(e.request,copy));return r}).catch(()=>caches.match(e.request).then(r=>r||caches.match("/"))))});'''
    return HttpResponse(source,content_type="application/javascript",headers={"Service-Worker-Allowed":"/"})
