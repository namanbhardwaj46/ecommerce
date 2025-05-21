"""
Find Test Orders

This script helps you find valid order IDs for testing the payment API.
It prints a list of orders with their IDs, status, and total amount.

Usage:
    python find_test_orders.py

Requirements:
    - Django
    - Access to the project's database
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

# Import models after Django setup
from orders.models import Order

def find_test_orders():
    """Find orders suitable for payment testing"""
    print("\n=== ORDERS AVAILABLE FOR PAYMENT TESTING ===\n")
    
    # Get all orders
    orders = Order.objects.all().order_by('-created_at')
    
    if not orders:
        print("No orders found in the database.")
        return
    
    # Print header
    print(f"{'ID':<40} | {'Status':<10} | {'Total':<10} | {'Paid':<10} | {'Remaining':<10}")
    print("-" * 90)
    
    # Print order details
    for order in orders:
        remaining = order.total - order.paid_amount
        status_display = order.get_status_display()
        
        # Highlight orders that can be paid
        can_pay = order.status in [Order.OrderStatus.PENDING, Order.OrderStatus.PARTIAL]
        prefix = "✅ " if can_pay else "❌ "
        
        print(f"{prefix}{order.id:<38} | {status_display:<10} | {order.total:<10} | {order.paid_amount:<10} | {remaining:<10}")
    
    print("\n✅ = Available for payment (pending or partial status)")
    print("❌ = Not available for payment\n")
    
    # Print instructions
    print("To use an order ID for payment testing:")
    print("1. Copy one of the IDs marked with ✅")
    print("2. Use it in your payment API call")
    print("3. Only orders with 'pending' or 'partial' status can accept payments\n")

if __name__ == "__main__":
    try:
        find_test_orders()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)