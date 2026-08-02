from django.db import transaction
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem, InsufficientStockError
from .forms import OrderCreateForm
from cart.cart import Cart
from shop.models import Product


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save()
                    for item in cart:
                        product = item['product']
                        updated = Product.objects.filter(
                            pk=product.pk, stock__gte=item['quantity']
                        ).update(stock=F('stock') - item['quantity'])
                        if not updated:
                            raise InsufficientStockError(product)
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            price=item['price'],
                            quantity=item['quantity']
                        )
                    order.total_cost = order.calculate_total_cost()
                    order.save(update_fields=['total_cost'])
            except InsufficientStockError as exc:
                return render(request, 'orders/order/create.html', {
                    'form': form,
                    'error_message': str(exc),
                })

            cart.clear()
            return redirect('orders:order_created', order_id=order.id)
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'form': form})


def order_created(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order/created.html', {'order': order})
