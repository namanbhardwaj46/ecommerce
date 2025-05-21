import razorpay # Razorpay SDK
from django.conf import settings # Access keys from settings
from .base import BasePaymentGateways   # Inherit interface
from razorpay.errors import SignatureVerificationError  # Specific exception
# from ecommerce import settings

class RazorpayGateway(BasePaymentGateways):
    def __init__(self):
        # Initialize Razorpay client with credentials
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )


    def get_payment(self, name, amount, currency, payment_id, order_id):
        """
        Creates a Razorpay hosted payment link.
        - Uses `payment_link.create()` instead of `order.create()`.
        - Returns the Razorpay hosted payment page URL.

        This method creates a payment link using `payment_link.create()` which returns a link that
        the customer can use to complete the payment.
        """
        try:
            payment_data = {
                "amount": int(amount * 100),  # Convert ₹1000 to 100000 paise
                "currency": currency,
                "reference_id": str(payment_id),  # Unique identifier for tracking the payment in your system.
                "description": f"Payment for Order #{order_id}",
                "customer": {
                    "name": f"{name}",
                    "email": "testuser@example.com",
                    "contact": "+917011882029"
                },
                "notify": {
                    "sms": True,
                    "email": True
                },
                "reminder_enable": True,
                "callback_url": "http://localhost:8000/api/payments/callback/",  # Webhook
                # "callback_url": "https://google.com/",
                # "callback_method": "post"  # ✅ Set to POST instead of GET
                # "callback_method": "get"
            }

            payment_link = self.client.payment_link.create(payment_data)  # Use Payment Links API
            return payment_link  # Returns full Razorpay response with checkout URL

        except Exception as e:
            raise ValueError(f"Failed to create payment link with Razorpay: {str(e)}")

    def confirm_payment(self, payment_id):
        """
        Fetch payment details from Razorpay.
        
        Args:
            payment_id: The Razorpay payment ID to confirm
            
        Returns:
            dict: The payment details from Razorpay
        """
        try:
            return self.client.payment_link.fetch(payment_id)
        except Exception as e:
            raise ValueError(f"Failed to fetch payment details from Razorpay: {str(e)}")
            
    def verify_payment(self, payment_data):
        """
        Confirm the payment by verifying the provided signature.

        The signature_data should include:
            - razorpay_order_id / payment_link_id,
            - payment_link_reference_id, payment_link_status,
            - razorpay_payment_id, and
            - razorpay_signature.

        Returns True if valid, False otherwise
        """
        try:
            self.client.utility.verify_payment_link_signature(payment_data)
            return True
        except SignatureVerificationError:
            return False