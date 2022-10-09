import os
import decimal
from distutils.sysconfig import get_makefile_filename
import random
import uuid
from .utils import unique_slug_generator


from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.utils.text import slugify
from django_countries.fields import CountryField

from .utils import round_decimals_down

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def upload_image_path(instance, filename):
    new_filename = random.randint(1,3910209312)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return "products/{0}/{1}".format(new_filename, final_filename)

CATEGORY_CHOICES = (
    ('LAPTOPS', 'Laptops'),
    ('COMPONENTS', 'Components'),
    ('MICE', 'Mice'),
    ('KEYBOARDS', 'Keyboards'),
    ('AUDIO', 'Audio'),
    ('STREAMING', 'Streaming'),
    ('CHAIRS', 'Chairs'),
    ('CONSOLE', 'Console'),
)


LABEL_CHOICES = (
    ('D', 'discount'),
    ('E', 'exclusive'),
    ('N', 'new'),
)

ORDER_STATUS_CHOICES = (
    ('P', 'Pending'),
    ('APAY', 'Awaiting Payment'),
    ('AF', 'Awaiting Fulfillment'),
    ('AS', 'Awaiting Shipment'),
    ('APU', 'Awaiting Pickup'),
    ('PS', 'Partially Shipped'),
    ('C', 'Completed'),
    ('S', 'Shipped'),
    ('CANC', 'Cancelled'),
    ('D', 'Declined'),
    ('R', 'Refunded'),
    ('PR', 'Partially Refunded')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)




class Item(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=20)
    discount_percent = models.FloatField(default=0 , null=True, blank=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=10, blank=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, blank=True, null=True)
    image = models.ImageField(upload_to=upload_image_path, default='thumbnail.png')
    detail_image = models.ImageField(upload_to=upload_image_path, default='thumbnail.png')
    summary = models.CharField(max_length=255, blank=False)
    posted = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=1000, blank=True)
    slug = models.SlugField(blank=True)

    
    def discount(self):
        if self.discount_percent > 0:
            discount_price = self.price - self.price * decimal.Decimal(self.discount_percent) / 100
            return round_decimals_down(discount_price, 2)

    def discount_badge(sender, instance, *args, **kwargs):
        if instance.discount_percent > 0:
            instance.label = 'D'
        else:
            instance.label = None

    def item_pre_save_receiver(sender, instance, *args, **kwargs):
        if not instance.slug:
            instance.slug = unique_slug_generator(instance)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product-detail", kwargs={
            'slug': self.slug
        })
    
    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def description_list(self):
        return self.description.split('\n')

    class Meta:
        ordering = ('-posted',)

pre_save.connect(Item.item_pre_save_receiver, sender=Item)
post_save.connect(Item.discount_badge, sender=Item)

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item')
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def price_with_out_discount(self):
        return self.item.price *  self.quantity

    def get_total_item_price(self):
        if self.item.discount_percent > 0:
            new_price = self.item.price - self.item.price * decimal.Decimal(self.item.discount_percent) / 100
        else:
            new_price = self.item.price
        total = new_price * self.quantity
        return round_decimals_down(total)




class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    created = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()    
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('Address', on_delete=models.SET_NULL, blank=True, null=True, related_name='billing_address')
    shipping_address = models.ForeignKey('Address', on_delete=models.SET_NULL, blank=True, null=True, related_name='shipping_address')
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.CASCADE, null=True, blank=True)
    ref_code = models.UUIDField(default=uuid.uuid4, unique=True)
    status = models.CharField(choices=ORDER_STATUS_CHOICES, max_length=4, default="P")

    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)


    def __str__(self):
        return self.user.username


    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return round_decimals_down(total, 2)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=True)
    zip = models.CharField(max_length=100)

    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField(max_length=255)


    def __str__(self):
        return f"{self.pk}"
