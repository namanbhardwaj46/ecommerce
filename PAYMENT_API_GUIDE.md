# Payment API Guide

This guide explains how to use the payment API in the ecommerce project.

## API Endpoints

- **Create Payment**: `POST /api/payments/create/`
- **Payment Callback**: `POST /api/payments/callback/`

## Creating a Payment

### Endpoint

```
POST /api/payments/create/
```

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| order | UUID | Yes | The UUID of an existing order |
| method | String | Yes | Payment method: 'wallet', 'upi', or 'card' |
| currency | String | No | Currency code (default: 'INR') |
| gateway | String | No | Payment gateway name (default: 'razorpay') |

### Example Request

```json
{
  "order": "550e8400-e29b-41d4-a716-446655440000",
  "method": "card",
  "currency": "INR",
  "gateway": "razorpay"
}
```

### Success Response (201 Created)

```json
{
  "payment_id": "550e8400-e29b-41d4-a716-446655440001",
  "gateway_order_id": "pay_L5T4eRgTJQi8NG",
  "order_id": "550e8400-e29b-41d4-a716-446655440000",
  "amount": 1000.00,
  "currency": "INR",
  "payment_link": "https://rzp.io/i/abcdefgh"
}
```

### Error Responses

#### 400 Bad Request

```json
{
  "error": "Payment processing issue: Invalid order ID"
}
```

#### 500 Internal Server Error

```json
{
  "error": "Database integrity error."
}
```

## Payment Flow

1. **Create Payment**:
   - Client sends a POST request to `/api/payments/create/` with order details
   - Server validates the order and creates a pending payment
   - Server initiates payment with Razorpay and returns a payment link

2. **Complete Payment**:
   - User follows the payment link to complete the payment on Razorpay's hosted page
   - After payment, Razorpay redirects to the callback URL

3. **Payment Callback**:
   - Razorpay sends a webhook to `/api/payments/callback/`
   - Server verifies the payment signature
   - Server updates the payment status and finalizes the order

## Implementation Examples

### Python Example

```python
import requests
import json

# API endpoint
url = "http://localhost:8000/api/payments/create/"

# Payment data
payment_data = {
    "order": "550e8400-e29b-41d4-a716-446655440000",  # Replace with actual order ID
    "method": "card",
    "currency": "INR",
    "gateway": "razorpay"
}

# Make the API call
response = requests.post(
    url,
    data=json.dumps(payment_data),
    headers={"Content-Type": "application/json"}
)

# Process the response
if response.status_code == 201:  # 201 Created
    payment_info = response.json()
    print("Payment created successfully!")
    print(f"Payment Link: {payment_info['payment_link']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### JavaScript Example

```javascript
// API endpoint
const url = 'http://localhost:8000/api/payments/create/';

// Payment data
const paymentData = {
  order: '550e8400-e29b-41d4-a716-446655440000',  // Replace with actual order ID
  method: 'card',
  currency: 'INR',
  gateway: 'razorpay'
};

// Make the API call
fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(paymentData),
})
.then(response => response.json())
.then(data => {
  console.log('Payment created successfully!');
  console.log('Payment Link:', data.payment_link);
  
  // Redirect to payment page
  window.location.href = data.payment_link;
})
.catch((error) => {
  console.error('Error:', error);
});
```

## Finding Order IDs

To get a valid order ID for testing:

1. **Django Admin Panel**:
   - Go to `/admin/orders/order/`
   - Find an order with 'pending' or 'partial' status
   - Copy the UUID

2. **Django Shell**:
   ```python
   python manage.py shell
   
   # In the shell
   from orders.models import Order
   
   # Get a pending order
   order = Order.objects.filter(status='pending').first()
   print(order.id)  # This is the UUID you need
   ```

## Important Notes

1. **Order Status**: The order must be in either 'pending' or 'partial' status to accept payments.

2. **Amount Validation**: The system automatically calculates the payment amount based on the order total and any previous payments.

3. **Payment Gateway**: Currently, only Razorpay is supported.

4. **Callback URL**: In production, ensure the callback URL is properly configured to receive webhooks from Razorpay.

5. **Testing**: Use Razorpay's test mode for development and testing.

## Troubleshooting

1. **Payment Creation Fails**:
   - Ensure the order exists and is in 'pending' or 'partial' status
   - Check that the order has items and a valid total amount

2. **Callback Not Received**:
   - Verify the callback URL is accessible from the internet
   - Check Razorpay webhook settings

3. **Payment Verification Fails**:
   - Ensure the Razorpay API keys are correctly configured
   - Check that the signature verification is working properly