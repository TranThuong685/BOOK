from rest_framework import serializers
from .models import *

        
class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetail
        fields = ('detail_id', 'color', 'size', 'quantity')
        
class ProductSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSale
        fields = ('price', 'start_date', 'end_date')


class ProductSerializer(serializers.ModelSerializer):
    productdetail_set = ProductDetailSerializer(many=True, read_only=True)
    productsale_set = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('product_id', 'name', 'description', 'productdetail_set', 'productsale_set', 'price', 'images', 'total_sold') 

    def get_productsale_set(self, obj):
        now = timezone.now()
        productsale = obj.productsale_set.filter( start_date__lte=now, end_date__gte=now).first()
        return ProductSaleSerializer(instance=productsale, many=False).data
    
    def get_images(self, obj):
        return [image.name.url for image in obj.productimage_set.all()]