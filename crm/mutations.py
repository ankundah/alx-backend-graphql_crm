import graphene
from django.core.exceptions import ValidationError
from django.db import transaction
from crm.models import Customer, Product, Order
from .schema import CustomerType, ProductType, OrderType
import re
from django.utils import timezone

# Single customer
class CreateCustomer(graphene.Mutation):
    customer = graphene.Field(CustomerType)
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    def mutate(self, info, name, email, phone=None):
        if Customer.objects.filter(email=email).exists():
            return CreateCustomer(success=False, message="Email already exists")
        if phone and not re.match(r"^\+?\d[\d\-]{7,}\d$", phone):
            return CreateCustomer(success=False, message="Invalid phone format")
        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, success=True, message="Customer created successfully")

# Bulk customers
class BulkCreateCustomers(graphene.Mutation):
    created_customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    class Arguments:
        customers = graphene.List(
            graphene.InputObjectType(
                "CustomerInput",
                name=graphene.String(required=True),
                email=graphene.String(required=True),
                phone=graphene.String(required=False)
            ),
            required=True
        )

    def mutate(self, info, customers):
        created = []
        errors = []
        with transaction.atomic():
            for cust in customers:
                name = cust.get("name")
                email = cust.get("email")
                phone = cust.get("phone", None)

                if Customer.objects.filter(email=email).exists():
                    errors.append(f"{email} already exists")
                    continue
                if phone and not re.match(r"^\+?\d[\d\-]{7,}\d$", phone):
                    errors.append(f"{email}: Invalid phone format")
                    continue
                try:
                    created_customer = Customer.objects.create(name=name, email=email, phone=phone)
                    created.append(created_customer)
                except Exception as e:
                    errors.append(f"{email}: {str(e)}")
        return BulkCreateCustomers(created_customers=created, errors=errors)

# Product
class CreateProduct(graphene.Mutation):
    product = graphene.Field(ProductType)
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            return CreateProduct(success=False, message="Price must be positive")
        if stock < 0:
            return CreateProduct(success=False, message="Stock cannot be negative")
        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product, success=True, message="Product created successfully")

# Order
class CreateOrder(graphene.Mutation):
    order = graphene.Field(OrderType)
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(success=False, message="Invalid customer ID")

        products = Product.objects.filter(pk__in=product_ids)
        if not products.exists():
            return CreateOrder(success=False, message="No valid products selected")

        if order_date is None:
            order_date = timezone.now()

        total_amount = sum([p.price for p in products])
        order = Order.objects.create(customer=customer, order_date=order_date, total_amount=total_amount)
        order.products.set(products)
        order.save()

        return CreateOrder(order=order, success=True, message="Order created successfully")
