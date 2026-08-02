from decimal import Decimal
from django.conf import settings
from shop.models import Product


class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0, 'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(
            id__in=product_ids).select_related('category')
        product_map = {str(product.id): product for product in products}

        # Drop cart entries for products that no longer exist (e.g. deleted)
        # so templates never see an item without a 'product' key.
        stale_ids = [pid for pid in self.cart if pid not in product_map]
        if stale_ids:
            for stale_id in stale_ids:
                del self.cart[stale_id]
            self.save()

        for product_id, item in self.cart.items():
            # Work on a copy: self.cart is a live reference into the
            # session data, and mutating it with a Decimal/Product would
            # break JSON session serialization on the next save().
            item = item.copy()
            item['product'] = product_map[product_id]
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
