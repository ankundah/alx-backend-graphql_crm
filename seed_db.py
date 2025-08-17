from django.core.management.base import BaseCommand
from crm.models import Customer, Product, Order
import random

class Command(BaseCommand):
    help = 'Seed the database with initial Customers, Products, and Orders'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # Customers
        customers_data = [
            {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
            {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
            {"name": "Carol", "email": "carol@example.com", "phone": "+1987654321"},
        ]

        customers = []
        for data in customers_data:
            customer, created = Customer.objects.get_or_create(email=data["email"], defaults=data)
            customers.append(customer)
        self.stdout.write(f"Created {len(customers)} customers")

        # Products
        products_data = [
            {"name": "Laptop", "price": 999.99, "stock": 10},
            {"name": "Phone", "price": 499.99, "stock": 20},
            {"name": "Keyboard", "price": 79.99, "stock": 50},
        ]

        products = []
        for data in products_data:
            product, created = Product.objects.get_or_create(name=data["name"], defaults=data)
            products.append(product)
        self.stdout.write(f"Created {len(products)} products")

        # Orders
        for customer in customers:
            order = Order.objects.create(
                customer=customer,
                total_amount=sum(p.price for p in products[:2])  # Randomly pick first 2 products
            )
            order.products.set(products[:2])
            order.save()

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
