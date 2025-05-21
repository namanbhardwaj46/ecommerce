import os
import django
import random
from decimal import Decimal

# Setup Django (only if you run separately)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from products.models import Product, Category
from orders.models import Order, OrderProduct
from users.models import User, Profile

# Clear existing data (optional, be careful!)
# User.objects.all().delete()
# Product.objects.all().delete()
# Category.objects.all().delete()
Order.objects.all().delete()
OrderProduct.objects.all().delete()

# Create Categories
# category_names = ['Electronics', 'Clothing', 'Books', 'Toys', 'Health & Beauty']
# categories = []
# for name in category_names:
#     cat, created = Category.objects.get_or_create(name=name)
#     categories.append(cat)
# print(f"✅ Created {len(categories)} Categories")

# Create Users
# users = []
# for i in range(10):
#     user = User.objects.create(name=f"User{i+1}")
#     profile = Profile.objects.create(
#         user=user,
#         address=f"Address {i + 1}",
#         phone=f"12345678{i:02d}",
#         email=f"user{i + 1}@example.com"
#     )
#     users.append(user)
# print(f"✅ Created {len(users)} Users")

# Fetch all users and categories
users = list(User.objects.all())
categories = list(Category.objects.all())
products = list(Product.objects.all())

# Create Products
# products = []
# for i in range(10):
#     product = Product.objects.create(
#         name=f"Product{i+1}",
#         price=Decimal(random.randint(100, 5000)),
#         description=f"Description for product {i+1}",
#         is_available=True,
#         category=random.choice(categories),
#         stock_quantity=random.randint(10, 50)
#     )
#     products.append(product)
# print(f"✅ Created {len(products)} Products")

# Create Orders
# for i in range(5):
#     order = Order.objects.create(
#         user=random.choice(users),
#         status=random.choice([Order.OrderStatus.PENDING, Order.OrderStatus.SUCCESS]),
#
#     )
#     # Add random products to the order
#     selected_products = random.sample(products, random.randint(1, 4))
#     for prod in selected_products:
#         OrderProduct.objects.create(
#             order=order,
#             product=prod,
#             quantity=random.randint(1, 5),
#             price_at_time=prod.price
#         )
# print(f"✅ Created 5 Orders with products")

print("🎉 Data population complete!")
