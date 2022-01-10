from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from shop.modifiers.pool import cart_modifiers_pool
from shop.modifiers.defaults import DefaultCartModifier
from shop.serializers.cart import ExtraCartRow
from shop.money import Money
from shop.shipping.modifiers import ShippingModifier
from shop_stripe import modifiers


class PrimaryCartModifier(DefaultCartModifier):
    """
    Extended default cart modifier which handles the price for product variations
    """

    def process_cart_item(self, cart_item, request):
        variant = cart_item.product.get_product_variant(
            product_code=cart_item.product_code)
        cart_item.unit_price = variant.unit_price
        cart_item.line_total = cart_item.unit_price * cart_item.quantity
        # grandparent super
        return super(DefaultCartModifier, self).process_cart_item(cart_item, request)


class PostalShippingModifier(ShippingModifier):
    """
    This is just a demo on how to implement a shipping modifier, which when selected
    by the customer, adds an additional charge to the cart.
    """
    identifier = 'postal-shipping'

    def get_choice(self):
        return (self.identifier, _("Postal shipping"))

    def add_extra_cart_row(self, cart, request):
        shipping_modifiers = cart_modifiers_pool.get_shipping_modifiers()
        if not self.is_active(cart.extra.get('shipping_modifier')) and len(shipping_modifiers) > 1:
            return
        # add a shipping flat fee
        amount = Money('5')
        instance = {'label': _("Shipping costs"), 'amount': amount}
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
        cart.total += amount

    def ship_the_goods(self, delivery):
        if not delivery.shipping_id:
            raise ValidationError("Please provide a valid Shipping ID")
        super().ship_the_goods(delivery)


class StripePaymentModifier(modifiers.StripePaymentModifier):
    commision_percentage = 3
