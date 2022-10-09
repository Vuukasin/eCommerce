from re import L
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


from .forms import CheckOutForm, RefundForm
from .models import Item, Order, OrderItem, Address, Payment, Refund
from django.views.generic import DetailView, View
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

import json

from django.conf import settings


import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid 



def home(request):
    new = Item.objects.filter(label="N")
    exclusive = Item.objects.filter(label="E")
    discount = Item.objects.filter(label="D")

    context = {
        'new_items': new[:4],
        'exclusive_items': exclusive[:4],
        'discounted_items': discount[:4]
    }

    return render(request, 'home.html', context)



class ProductAdded(LoginRequiredMixin, DetailView):
    model = Item
    template_name = 'product_added.html'
    



class ItemDetailView(DetailView):
    
    model = Item
    template_name = "product.html"



@login_required()
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
    return redirect("core:product-added", slug=slug)

@login_required()
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            order_item.delete()
        else:
            return redirect("core:cart")
    else:
        return redirect("core:cart")
    return redirect("core:cart")

@login_required()
def decrease_quantity(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            return redirect('core:cart')
        else:
            return redirect('core:cart')
    else:
        return redirect('core:cart')

@login_required()
def increase_quantity(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order_item.quantity += 1
            order_item.save()
        return redirect('core:cart')
    return redirect('core:cart')


class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order': order
            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            return render(self.request, 'cart.html')





class CheckoutView(LoginRequiredMixin ,View):
    def get(self, *args, **kwargs):
        try:
            form = CheckOutForm()
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'form': form,
                'order': order
            }

            shipping_address_qs = Address.objects.filter(user=self.request.user, address_type='S', default=True)
            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(user=self.request.user, address_type='B', default=True)
            if billing_address_qs.exists():
                context.update({'default_billing_address': billing_address_qs[0]})

            return render(self.request, 'checkout.html', context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You dont have an active order")
            return render(self.request, 'cart.html')
        
    def post(self, *args, **kwargs):
        form = CheckOutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    print("Using default shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "No default shipping address available")
                        return redirect('core:chcekout')
                else:
                    print("User entering new a new shipping address")
                    shipping_address1 = form.cleaned_data.get('shipping_address1')
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(self.request, "Please fill in required shipping address fields")  

                use_default_billing = form.cleaned_data.get('use_default_billing')
                same_billing_address = form.cleaned_data.get('same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using default billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request, "No default billing address")
                        return redirect('core:checkout')
                else:
                    print("User entering a new billing address")
                    billing_address1 = form.cleaned_data.get('billing_address1')
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get('set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(self.request, "Please fill in the required billing address fields")
                
                

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:paymant', payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect('core:checkout')

            order.status = "APAY"
            order.save()

        except ObjectDoesNotExist:
            messages.warning(self.request, "You may not have an active order")
            return redirect('core:home')


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, 'payment.html', context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        print("token:", token)
        amount = int(order.get_total() * 100)

        try:
            charge = stripe.Charge.create(
                amount = amount,
                currency = 'usd',
                source = token,
            )
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order.ordered = True
            order.payment = payment
            order.status = "AF"
            order.save()

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            messages.success("Your order was successful!")
            return redirect('core:home')

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")
            
        except stripe.error.RateLimitError as e:
            messages.error(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            messages.error(self.request, "Invalid parametars")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            messages.error(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            messages.error(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            messages.error(self.request, "Something went wrong. You are not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            messages.error(self.request, "A serious error occured, We have been notifed")
            return redirect('core:home')

class RequestRefundView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)
    def post(self, *args, **kwargs):
        form = RefundForm()
        if form.is_valid():
            ref_code = form.cleaned_data.get("ref_code")
            message = form.cleaned_data.get("message")
            email = form.cleaned_data.get("email")
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received")
                return redirect("core:request-refund")
            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exists")
                return redirect("core:request-refund")
                
    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()
            
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received")
                return redirect('core:request-refund')

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exists")
                return redirect('core:request-refund')

class OrdersView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            orders = Order.objects.filter(user=self.request.user)
            print(orders)
            context = {
                'orders': orders
            }
            return render(self.request, 'orders.html', context)
        except ObjectDoesNotExist:
            pass




def mice_view(request):
    items = Item.objects.filter(category="MICE")

    context = {
        'items': items
    }
    return render(request, 'products/gaming-mice.html', context)

def keyboard_view(request):
    items = Item.objects.filter(category="KEYBOARDS")
    context = {
        'items': items
    }
    return render(request, 'products/gaming-keyboards.html', context)

def components_view(request):
    items = Item.objects.filter(category="COMPONENTS")
    context = {
        'items': items
    }
    return render(request, 'products/components.html', context)

def laptops_view(request):
    items = Item.objects.filter(category="LAPTOPS")
    context = {
        'items': items
    }
    return render(request, 'products/gaming-laptops.html', context)

def audio_view(request):
    items = Item.objects.filter(category="AUDIO")
    context = {
        'items': items
    }
    return render(request, 'products/gaming-audio.html', context)

def streaming_view(request):
    items = Item.objects.filter(category="STREAMING")
    context = {
        'items': items
    }
    return render(request, 'products/streaming.html', context)

def chairs_view(request):
    items = Item.objects.filter(category="CHAIRS")
    context = {
        'items': items
    }
    return render(request, 'products/gaming-chairs.html', context)

def console_view(request):
    items = Item.objects.filter(category="CONSOLE")
    context = {
        'items': items
    }
    return render(request, 'products/console.html', context)

def new_items_view(request):
    items = Item.objects.filter(label="N")
    context = {
        'items': items
    }
    return render(request, 'products/new-items.html', context)

def last_chance_view(request):
    items = Item.objects.filter(label='D')
    context = {
        'items': items
    }
    return render(request, 'products/last-chance.html', context)

def exclusives_view(request):
    items = Item.objects.filter(label="E")
    context = {
        'items': items
    }
    return render(request, 'products/exclusives.html', context)
