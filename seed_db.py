import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_database():
    print("Seeding database...")
    
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()
    
    customers = [
        {"name": "Alice Johnson", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob Smith", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol Davis", "email": "carol@example.com", "phone": "+9876543210"},
    ]
    
    for customer_data in customers:
        customer = Customer.objects.create(**customer_data)
        print(f"Created customer: {customer.name}")
    
    products = [
        {"name": "Laptop", "price": Decimal("999.99"), "stock": 10},
        {"name": "Phone", "price": Decimal("599.99"), "stock": 25},
        {"name": "Tablet", "price": Decimal("399.99"), "stock": 15},
        {"name": "Headphones", "price": Decimal("199.99"), "stock": 50},
    ]
    
    for product_data in products:
        product = Product.objects.create(**product_data)
        print(f"Created product: {product.name}")
    
    alice = Customer.objects.get(name="Alice Johnson")
    bob = Customer.objects.get(name="Bob Smith")
    
    laptop = Product.objects.get(name="Laptop")
    phone = Product.objects.get(name="Phone")
    tablet = Product.objects.get(name="Tablet")
    headphones = Product.objects.get(name="Headphones")
    
    order1 = Order.objects.create(customer=alice)
    order1.products.set([laptop, headphones])
    order1.save()
    print(f"Created order for {alice.name}: Laptop + Headphones")
    
    order2 = Order.objects.create(customer=bob)
    order2.products.set([phone, tablet])
    order2.save()
    print(f"Created order for {bob.name}: Phone + Tablet")
    
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()