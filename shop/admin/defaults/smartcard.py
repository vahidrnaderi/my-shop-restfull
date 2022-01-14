from django.contrib import admin
# from adminsortable2.admin import SortableAdminMixin
# from shop.admin.product import CMSPageAsCategoryMixin, ProductImageInline, InvalidateProductCacheMixin
from shop.admin.product import ProductImageInline, InvalidateProductCacheMixin
# from myshop.models import SmartCard
from shop.shopmodels.defaults.smartcard import SmartCard


@admin.register(SmartCard)
# class SmartCardAdmin(InvalidateProductCacheMixin, SortableAdminMixin, CMSPageAsCategoryMixin, admin.ModelAdmin):
class SmartCardAdmin(InvalidateProductCacheMixin, admin.ModelAdmin):
    fields = ['product_name', 'slug', 'product_code', 'unit_price', 'active', 'caption', 'description',
              'storage', 'card_type']
    inlines = [ProductImageInline]
    prepopulated_fields = {'slug': ['product_name']}
    list_display = ['product_name', 'product_code', 'unit_price', 'active']
