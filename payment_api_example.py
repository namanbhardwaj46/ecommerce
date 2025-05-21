"""
Payment API Example

This script demonstrates how to make a payment API call to the ecommerce project.
It shows how to:
1. Create a payment for an existing order
2. Handle the response from the payment API
3. Use the payment link to complete the payment

Usage:
    python payment_api_example.py

Requirements:
    - requests library: pip install requests
    - An existing order in the database
"""

import requests
import json
import uuid  # For generating test order IDs if needed

# API endpoint for creating a payment
BASE_URL = "http://localhost:8000/api"  # Change this to your actual server URL
PAYMENT_CREATE_URL = f"{BASE_URL}/payments/create/"

# Function to create a payment
def create_payment(order_id, method="card", currency="INR", gateway="razorpay"):
    """
    Create a payment for an order.
    
    Args:
        order_id (str): The UUID of the order to pay for
        method (str): Payment method - 'wallet', 'upi', or 'card'
        currency (str): Currency code, default is 'INR'
        gateway (str): Payment gateway name, default is 'razorpay'
        
    Returns:
        dict: The payment response data or error message
    """
    # Payment data according to the PaymentSerializer requirements
    payment_data = {
        "order": order_id,  # UUID of an existing order
        "method": method,   # One of: 'wallet', 'upi', 'card'
        "currency": currency,
        "gateway": gateway
    }
    
    # Print the request data for debugging
    print(f"Sending payment request: {json.dumps(payment_data, indent=2)}")
    
    try:
        # Make the API call
        response = requests.post(
            PAYMENT_CREATE_URL,
            json=payment_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        if response.status_code == 201:  # 201 Created
            payment_info = response.json()
            print("\nPayment created successfully!")
            print(f"Payment ID: {payment_info['payment_id']}")
            print(f"Gateway Order ID: {payment_info['gateway_order_id']}")
            print(f"Order ID: {payment_info['order_id']}")
            print(f"Amount: {payment_info['amount']}")
            print(f"Currency: {payment_info['currency']}")
            print(f"Payment Link: {payment_info['payment_link']}")
            print("\nUse the payment link to complete the payment.")
            return payment_info
        else:
            print(f"\nError: {response.status_code}")
            print(response.json())
            return {"error": response.json()}
            
    except requests.exceptions.RequestException as e:
        print(f"\nRequest error: {str(e)}")
        return {"error": str(e)}
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    # Replace this with an actual order ID from your database
    # You can get this from the Django admin panel or by querying the database
    test_order_id = "your-order-uuid-here"  # Replace with a real order ID
    
    # Uncomment the line below to use the example
    # payment_response = create_payment(test_order_id)
    
    print("\n=== PAYMENT API EXAMPLE ===")
    print("To use this example:")
    print("1. Replace 'your-order-uuid-here' with a real order ID from your database")
    print("2. Uncomment the 'payment_response = create_payment(test_order_id)' line")
    print("3. Run the script: python payment_api_example.py")
    print("\nNote: The order must be in 'pending' or 'partial' status to accept payments.")