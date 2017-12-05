from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class Customer(models.Model):
    full_name = models.CharField(max_length=1000)
    company_name = models.CharField(max_length=1000)
    email = models.EmailField(max_length=1000)
    address = models.CharField(max_length=1000)
    postal_code = models.CharField(max_length=1000)
    city = models.CharField(max_length=1000)
    country = models.CharField(max_length=1000)

    def __str__(self):
        return self.full_name

    def to_search(self):
        d = {
            '_id': self.pk,
            'full_name': self.full_name,
            'company_name': self.company_name,
            'email': self.email,
            'address': self.address,
            'postal_code': self.postal_code,
            'city': self.city,
            'country': self.country,
        }
        if hasattr(self, 'total_orders'):
            d['total_orders'] = self.total_orders
        return d

    class Meta:
        managed = False
        db_table = 'customers'


class OrderLine(models.Model):
    # watch out, hack: Django *really* wants a primary key, so we
    # pretend that "order_id" is it. This should be ok as long
    # as we only use this for read access
    order = models.ForeignKey('Order', models.DO_NOTHING, primary_key=True)
    product = models.ForeignKey('Product', models.DO_NOTHING)
    amount = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'order_lines'


class Order(models.Model):
    customer = models.ForeignKey(Customer, models.DO_NOTHING, related_name='orders')
    created_at = models.DateTimeField(default=timezone.now)
    lines = models.ManyToManyField('Product', through=OrderLine)

    class Meta:
        managed = False
        db_table = 'orders'

    def to_search(self):
        order_lines = list(self.orderline_set.all())
        return {
            '_id': self.pk,
            'customer': {
                'id': self.customer.pk,
                'full_name': self.customer.full_name,
            },
            'created_at': self.created_at,
            'data': {
                'total_amount': sum(line.product.selling_price for line in order_lines) / 100.0,
                'cost': sum(line.product.cost for line in order_lines) / 100.0,
                'margin': sum((line.product.selling_price - line.product.cost) for line in order_lines) / 100.0,
            }
        }


class ProductType(models.Model):
    name = models.CharField(unique=True, max_length=1000)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'product_types'


class Product(models.Model):
    sku = models.CharField(unique=True, max_length=1000)
    name = models.CharField(max_length=1000)
    description = models.TextField()
    product_type = models.ForeignKey(ProductType, models.DO_NOTHING, db_column='type_id')
    stock = models.IntegerField()
    cost = models.IntegerField()
    selling_price = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'products'
