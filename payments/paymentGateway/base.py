from abc import ABC, abstractmethod # Base class for gateway interface


class BasePaymentGateways(ABC):
    @abstractmethod
    def get_payment(self, name, amount, currency, payment_id, order_id): pass # Create order in gateway and get payment details.
    @abstractmethod
    def verify_payment(self, payment_data): pass    # Verify callback data authenticity.
    @abstractmethod
    def confirm_payment(self, payment_id): pass    # Confirm the payment by verifying callback data