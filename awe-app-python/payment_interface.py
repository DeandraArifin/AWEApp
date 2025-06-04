from abc import ABC, abstractmethod
from models import PaymentMethod, Receipt, OrderSubject, ReceiptCreator
import datetime

class PaymentStrategy(ABC):
    @abstractmethod
    def process_payment(self, order, session):
        pass

class CreditCardPayment(PaymentStrategy):
    def process_payment(self, order, session):
        print(f"Processing credit card payment for Order #{order.id}")
        receipt = Receipt(
            order_id=order.id,
            customer_id=order.customer_id,
            payment_method=PaymentMethod.CREDITCARD,
            payment_dt=datetime.datetime.utcnow(),
            total=order.total
        )
        session.add(receipt)
        session.commit()

        subject = OrderSubject(order)
        subject.attach(ReceiptCreator())
        subject.set_status("PROCESSING", session)

class BankTransferPayment(PaymentStrategy):
    def process_payment(self, order, session):
        print(f"Processing bank transfer payment for Order #{order.id}")
        receipt = Receipt(
            order_id=order.id,
            customer_id=order.customer_id,
            payment_method=PaymentMethod.BANKTRANSFER,
            payment_dt=datetime.datetime.utcnow(),
            total=order.total
        )
        session.add(receipt)
        session.commit()

        subject = OrderSubject(order)
        subject.attach(ReceiptCreator())
        subject.set_status("PROCESSING", session)


class PayPalPayment(PaymentStrategy):
    def process_payment(self, order, session):
        print(f"Processing PayPal payment for Order #{order.id}")
        receipt = Receipt(
            order_id=order.id,
            customer_id=order.customer_id,
            payment_method=PaymentMethod.PAYPAL,
            payment_dt=datetime.datetime.utcnow(),
            total=order.total
        )
        session.add(receipt)
        session.commit()

        subject = OrderSubject(order)
        subject.attach(ReceiptCreator())
        subject.set_status("PROCESSING", session)

class CashOnDeliveryPayment(PaymentStrategy):
    def process_payment(self, order, session):
        print(f"Processing cash on delivery payment for Order #{order.id}")
        receipt = Receipt(
            order_id=order.id,
            customer_id=order.customer_id,
            payment_method=PaymentMethod.CASHONDELIVERY,
            payment_dt=datetime.datetime.utcnow(),
            total=order.total
        )
        session.add(receipt)
        session.commit()

        subject = OrderSubject(order)
        subject.attach(ReceiptCreator())
        subject.set_status("PROCESSING", session)