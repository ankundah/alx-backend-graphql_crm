import re
from datetime import datetime
import graphene
from graphene_django import DjangoObjectType
from django.db import transaction, IntegrityError
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .mutations import CreateCustomer, BulkCreateCustomers, CreateProduct, CreateOrder
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filterset_class = CustomerFilter
        fields = ("id", "name", "email", "phone")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filterset_class = ProductFilter
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filterset_class = OrderFilter
        fields = ("id", "customer", "products", "total_amount", "order_date")

# Query
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType)
    all_products = DjangoFilterConnectionField(ProductType)
    all_orders = DjangoFilterConnectionField(OrderType)



# -----------------------------
# Mutations
# -----------------------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(root, info, name, email, phone=None):
        # Validate phone
        if phone and not re.match(r"^\+?\d[\d\-]{7,}\d$", phone):
            return CreateCustomer(customer=None, message="Invalid phone format")

        # Validate email uniqueness
        if Customer.objects.filter(email=email).exists():
            return CreateCustomer(customer=None, message="Email already exists")

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    class CustomerInput(graphene.InputObjectType):
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String()

    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        created_customers = []
        errors = []

        for cust_data in input:
            name = cust_data.name
            email = cust_data.email
            phone = cust_data.phone

            # Validate phone
            if phone and not re.match(r"^\+?\d[\d\-]{7,}\d$", phone):
                errors.append(f"Invalid phone format for {email}")
                continue

            if Customer.objects.filter(email=email).exists():
                errors.append(f"Email already exists: {email}")
                continue

            customer = Customer(name=name, email=email, phone=phone)
            customer.save()
            created_customers.append(customer)

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(default_value=0)

    product = graphene.Field(ProductType)
    message = graphene.String()

    def mutate(root, info, name, price, stock=0):
        if price <= 0:
            return CreateProduct(product=None, message="Price must be positive")
        if stock < 0:
            return CreateProduct(product=None, message="Stock cannot be negative")

        product = Product(name=name, price=price, stock=stock)
        product.save()
        return CreateProduct(product=product, message="Product created successfully")


class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime()

    order = graphene.Field(OrderType)
    message = graphene.String()

    def mutate(root, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(order=None, message="Customer not found")

        if not product_ids:
            return CreateOrder(order=None, message="No products provided")

        products = Product.objects.filter(id__in=product_ids)
        if not products.exists():
            return CreateOrder(order=None, message="Invalid product IDs")

        total_amount = sum([p.price for p in products])
        order = Order(customer=customer, total_amount=total_amount, order_date=order_date or datetime.now())
        order.save()
        order.products.set(products)
        return CreateOrder(order=order, message="Order created successfully")


# -----------------------------
# Root Mutation
# -----------------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


# -----------------------------
# Root Query (empty placeholder)
# -----------------------------
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

