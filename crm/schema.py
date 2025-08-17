import graphene
from graphene_django import DjangoObjectType
# from django.core.exceptions import ValidationError
# from django.db import transaction
from crm.models import Customer, Product, Order
from .mutations import CreateCustomer, BulkCreateCustomers, CreateProduct, CreateOrder

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")  # optional test field

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Heyyyy Thia!")

schema = graphene.Schema(query=Query)
