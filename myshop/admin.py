from django.contrib import admin
from django.template.context import Context
from django.template.loader import get_template
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from parler.admin import TranslatableAdmin
from filer.models import ThumbnailOption
from cms.admin.placeholderadmin import PlaceholderAdminMixin, FrontendEditableAdminMixin
from shop.admin.defaults import customer
from shop.admin.defaults.order import OrderAdmin
from shop.models.defaults.order import Order
from shop.admin.order import PrintInvoiceAdminMixin
from shop.admin.delivery import DeliveryOrderAdminMixin
from shop_sendcloud.admin import SendCloudOrderAdminMixin
from adminsortable2.admin import SortableAdminMixin, PolymorphicSortableAdminMixin
from shop.admin.product import CMSPageAsCategoryMixin, UnitPriceMixin, ProductImageInline, InvalidateProductCacheMixin, SearchProductIndexMixin, CMSPageFilter
from polymorphic.admin import (PolymorphicParentModelAdmin, PolymorphicChildModelAdmin,
                               PolymorphicChildModelFilter)
from myshop.models import Product, Commodity, SmartPhoneVariant, SmartPhoneModel, OperatingSystem
from myshop.models import Manufacturer, SmartCard
from myshop.models import CommodityInventory, SmartCardInventory, SmartPhoneInventory


admin.site.site_header = "My SHOP Administration"
admin.site.unregister(ThumbnailOption)


@admin.register(Order)
class OrderAdmin(PrintInvoiceAdminMixin, SendCloudOrderAdminMixin, DeliveryOrderAdminMixin, OrderAdmin):
    pass


admin.site.register(Manufacturer, admin.ModelAdmin)

__all__ = ['customer']


class CommodityInventoryAdmin(admin.StackedInline):
    model = CommodityInventory
    extra = 0


class SmartCardInventoryAdmin(admin.StackedInline):
    model = SmartCardInventory
    extra = 0


@admin.register(Commodity)
class CommodityAdmin(InvalidateProductCacheMixin, SearchProductIndexMixin, SortableAdminMixin, TranslatableAdmin, FrontendEditableAdminMixin,
                     PlaceholderAdminMixin, CMSPageAsCategoryMixin, PolymorphicChildModelAdmin):
    """
    Since our Commodity model inherits from polymorphic Product, we have to redefine its admin class.
    """
    base_model = Product
    fields = [
        ('product_name', 'slug'),
        ('product_code', 'unit_price'),
        'active',
        'caption',
        'manufacturer',
    ]
    filter_horizontal = ['cms_pages']
    inlines = [ProductImageInline, CommodityInventoryAdmin]
    prepopulated_fields = {'slug': ['product_name']}


@admin.register(SmartCard)
class SmartCardAdmin(InvalidateProductCacheMixin, SearchProductIndexMixin, SortableAdminMixin, TranslatableAdmin, FrontendEditableAdminMixin,
                     CMSPageAsCategoryMixin, PlaceholderAdminMixin, PolymorphicChildModelAdmin):
    base_model = Product
    fieldsets = (
        (None, {
            'fields': [
                ('product_name', 'slug'),
                ('product_code', 'unit_price'),
                'active',
            ],
        }),
        (_("Translatable Fields"), {
            'fields': ['caption', 'description'],
        }),
        (_("Properties"), {
            'fields': ['manufacturer', 'storage', 'card_type', 'speed'],
        }),
    )
    filter_horizontal = ['cms_pages']
    inlines = [ProductImageInline, SmartCardInventoryAdmin]
    prepopulated_fields = {'slug': ['product_name']}


admin.site.register(OperatingSystem, admin.ModelAdmin)


class SmartPhoneInline(admin.TabularInline):
    model = SmartPhoneVariant
    extra = 0

    class Media:
        js = ['shop/js/admin/popup.js']

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        readonly_fields.append('variant_admin')
        return readonly_fields

    def variant_admin(self, obj):
        link = reverse('admin:myshop_smartphonevariant_change',
                       args=(obj.id,)), _("Edit Variant")
        return format_html(
            '<span class="object-tools"><a href="#" onclick="shopShowAdminPopup(\'{0}\', \'Edit Variant\');" class="viewsitelink">{1}</a></span>',
            *link)
    variant_admin.short_display = _("Edit Variant")


@admin.register(SmartPhoneModel)
class SmartPhoneAdmin(InvalidateProductCacheMixin, SearchProductIndexMixin, SortableAdminMixin, TranslatableAdmin, FrontendEditableAdminMixin,
                      CMSPageAsCategoryMixin, PlaceholderAdminMixin, PolymorphicChildModelAdmin):
    base_model = Product
    fieldsets = [
        (None, {
            'fields': [
                ('product_name', 'slug'),
                'active',
            ],
        }),
        (_("Translatable Fields"), {
            'fields': ['caption', 'description'],
        }),
        (_("Properties"), {
            'fields': ['manufacturer', 'battery_type', 'battery_capacity', 'ram_storage',
                       'wifi_connectivity', 'bluetooth', 'gps', 'operating_system',
                       ('width', 'height', 'weight',), 'screen_size'],
        }),
    ]
    filter_horizontal = ['cms_pages']
    inlines = [ProductImageInline, SmartPhoneInline]
    prepopulated_fields = {'slug': ['product_name']}

    def render_text_index(self, instance):
        template = get_template('search/indexes/myshop/commodity_text.txt')
        return template.render(Context({'object': instance}))
    render_text_index.short_description = _("Text Index")


class SmartPhoneInventoryAdmin(admin.StackedInline):
    model = SmartPhoneInventory


@admin.register(SmartPhoneVariant)
class SmartPhoneVariantAdmin(admin.ModelAdmin):
    inlines = [SmartPhoneInventoryAdmin]
    exclude = ['product']

    def has_module_permission(self, request):
        return False


@admin.register(Product)
class ProductAdmin(PolymorphicSortableAdminMixin, PolymorphicParentModelAdmin):
    base_model = Product
    child_models = [SmartPhoneModel, SmartCard, Commodity]
    list_display = ['product_name', 'get_price', 'product_type', 'active']
    list_display_links = ['product_name']
    search_fields = ['product_name']
    list_filter = [PolymorphicChildModelFilter, CMSPageFilter]
    list_per_page = 250
    list_max_show_all = 1000

    def get_price(self, obj):
        return str(obj.get_real_instance().get_price(None))

    get_price.short_description = _("Price starting at")
