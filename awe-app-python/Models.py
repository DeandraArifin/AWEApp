from enum import Enum as PyEnum
import datetime
from sqlalchemy import create_engine, Float, Column, Integer, String, Enum, ForeignKey, null, UniqueConstraint, DateTime, Boolean
from sqlalchemy.orm import relationship, Session
from urllib.parse import quote_plus
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

original_password = '@Sunshine123'
encoded_password = quote_plus(original_password)

engine = create_engine(f'mysql+mysqlconnector://admin:Sunshine123@awe-app-db.cxm864cy2rlj.ap-southeast-2.rds.amazonaws.com:3306/awe_app')


class AccountType(PyEnum):
    CUSTOMER = 'CUSTOMER'
    ADMIN = 'ADMIN'

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_on' : account_type
    }
    
    def __init__(self, username, password_hash, full_name, email, account_type: AccountType):
        self.username = username
        self.password_hash = password_hash
        self.full_name = full_name
        self.email = email
        self.account_type = account_type
    
    def authenticate(self, username: str, password:str):
        return self.username == username and self.password_hash == password
    
    def get_email(self):
        return self.email
    
    def get_name(self):
        return self.full_name
        

class Customer(Account):
    
    __tablename__ = 'customers'
    
    id = Column(Integer, ForeignKey('accounts.id'), primary_key=True)
    shipping_address = Column(String(255), nullable=False)
    phone_number = Column(String(10), nullable=False) #standard aussie phone number has 10 digits
    #order histoy
    cart = relationship('ShoppingCart', back_populates='owner', uselist=False, cascade='all, delete-orphan')
    orders = relationship('Order', back_populates='customer')
    
    __mapper_args__ = {
        'polymorphic_identity': AccountType.CUSTOMER
    }
    
    def __init__(self, username, password_hash, full_name, email, account_type, shipping_address, phone_number):
        super().__init__(username, password_hash, full_name, email, AccountType.CUSTOMER)
        self.shipping_address = shipping_address
        self.phone_number = phone_number
        self.cart = ShoppingCart()
    
    
    def get_order_history(self):
        return list(self.orders) #maybe change to spit out a list instead
    
class Admin(Account):
    
    __tablename__ = 'admins'
    
    id = Column(Integer, ForeignKey('accounts.id'), primary_key=True)
    employee_id = Column(Integer, nullable=False, unique=True)
    
    __mapper_args__ = {
        'polymorphic_identity': AccountType.ADMIN # or "admin", depending on your enum
    }
    
    
    def __init__(self, username, password_hash, full_name, email, account_type, employee_id):
        super().__init__(username, password_hash, full_name, email, account_type)
        self.employee_id = employee_id
        
    #maybe define a getter function for employee id?
 
class ProductCategory(PyEnum):
    SMARTPHONES = "SMARTPHONES"
    LAPTOPS = "LAPTOPS"
    TABLETS = "TABLETS"
    TELEVISIONS = "TELEVISIONS"
    CAMERAS = "CAMERAS"
    AUDIO = "AUDIO"
    ACCESSORIES = "ACCESSORIES"
    
class ProductDecorator:
    def __init__(self, product):
        self._product = product
    
    def get_price(self):
        return self._product.price
        
# class SaleDecorator(ProductDecorator):
#     def get_price(self):
        

class Product(Base):
    
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    category = Column(Enum(ProductCategory), nullable=False)
    on_sale = Column(Boolean, default=False, nullable=False )
    discount_percentage = Column(Integer, nullable=True, default=0)
    
    def update_description(self, new_description):
        if(new_description):
            self.description = new_description
        else:
            raise ValueError("New description cannot be empty")
    
    def get_stock(self):
        return self.stock
    
    def set_stock(self, new_stock):
        self.stock = new_stock
        
class ProductCatalogue():
    def __init__(self, session: Session):
        self.session = session
    
    def get_all_products(self):
        return self.session.query(Product).all()
    
    def add_product(self, product: Product):
        self.session.add(product)
        self.session.commit()
        
    def remove_product(self, product_id:int):
        product = self.session.get(Product,product_id)
        if(product):
            self.session.delete(product)
            self.session.commit()
    
    def search_by_category(self, category: ProductCategory):
        return self.session.query(Product).filter_by(category=category)
    
    def search_by_price_range(self, min_price: float, max_price: float):
        return self.session.query(Product).filter(
            Product.price >= min_price,
            Product.price <= max_price
        ).all()
        
    def get_product_details(self, product_id:int):
        product = self.session.get(Product,product_id)
        if(product):
            return(product.name, product.description, product.price)
        return None
    
class OrderStatus(PyEnum):
    PENDING = 'PENDING'
    IN_PROCESS = 'IN PROCESS'
    SHIPPED = 'SHIPPED'
    DELIVERED = 'DELIVERED'

class CartDecorator:
    def __init__(self, cart):
        self._cart = cart
    
    def get_total(self):
        return self._cart.calculate_total()

class TaxDecorator(CartDecorator):
    def get_total(self):
        return self._cart.calculate_total() * 1.1 #assumes 10% tax

class ShoppingCart(Base):
    __tablename__= 'shopping_carts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    owner = relationship('Customer', back_populates='cart', uselist=False)
    items = relationship('CartItem', back_populates='cart', cascade='all, delete-orphan') 
    
    def add_item_quantity(self, product: Product, session: Session):
        #check if the product is already a cart item in this cart
        for item in self.items:
            if item.product_id == product.id:
                item.quantity += 1
                session.commit()
            return
        
        #if not, then it's added as a cart item
        self.items.append(CartItem(self, product))
    
    def reduce_item_quantity(self, product: Product, session: Session):
        
        for item in self.items:
            if item.product_id == product.id:
                #if the quantity of the product in the cart is greater than the amount
                #that the customer wants to reduce it by (e.g. remove one of 2 items)
                if item.quantity > 1:
                    item.quantity -= 1
                else:
                    self.items.remove(item)
                session.commit()
                break
                
    
    def calculate_total(self) -> float:
        return sum(item.calculate_subtotal() for item in self.items)
    
    def checkout(self, session, customer_id, full_name, email, shipping_address, phone_number):
        #checks if cart is empty
        if not self.items:
            raise ValueError("Cannot checkout an empty cart")
    
        if not full_name or not email:
            raise ValueError("Guest checkout requires full_name and email") #implement input validation in UI too
        
        taxed_cart = TaxDecorator(self)
        taxed_total = taxed_cart.get_total()
        
        order = Order(
            customer_id = customer_id,
            full_name = full_name,
            email = email,
            phone_number = phone_number,
            shipping_address = shipping_address,
            total = taxed_total,
            status = OrderStatus.PENDING
        )
        
        for item in self.items:
            order_item = OrderItem(
                product_id = item.product_id,
                quantity = item.quantity,
                price = item.calculate_subtotal()
            )
            order.items.append(order_item)
        session.add(order)
        session.flush() #ensures order id is created
        
        order_subject = OrderSubject(order)
        order_subject.attach(InvoiceCreator())
        order_subject.set_status(OrderStatus.PENDING, session)
            
        
        session.commit()
        return order
    
    def empty_cart(self, session):
        
        for item in self.items[:]:
            session.delete(item)
            
        self.items.clear()
        session.commit()

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey('shopping_carts.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    
    cart = relationship('ShoppingCart', back_populates='items')
    product = relationship('Product')
    
    __table_args__ = (
        UniqueConstraint('cart_id', 'product_id', name='unique_cart_product'),
    )
    
    def __init__(self, cart: ShoppingCart, product: Product):
        self.cart_id = cart.id
        self.product_id = product.id
        self.quantity = 1
    
    def calculate_subtotal(self) -> float:
        total = self.product.price * self.quantity
        return total

class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    order = relationship('Order', back_populates='items')
    product = relationship('Product')
    
class Order(Base):
    __tablename__ ='orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone_number = Column(Integer, nullable=False)
    shipping_address = Column(String(255), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False)
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    customer = relationship('Customer', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    
    def __init__(self, customer_id, full_name, email, phone_number, shipping_address, status, total):
        self.customer_id = customer_id
        self.full_name = full_name
        self.email = email
        self.phone_number = phone_number
        self.shipping_address = shipping_address
        self.status = status
        self.total = total
        
    def get_total_sum(self):
        return self.total
        
class Invoice(Base):
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    email = Column(String(255), nullable=False)
    total = Column(Integer, nullable=False)
    
    #add functionality to generate and email receipts to customers
    
class PaymentMethod(PyEnum):
    CREDITCARD = 'CREDITCARD'
    BANKTRANSFER = 'BANKTRANSFER'

class Receipt(Base):
    __tablename__ = 'receipts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    # payment_id = Column(Integer, ForeignKey('payments.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    
    #assumes that receipt is auto-generated upon payment, therefore the current date and time is used
    payment_dt = Column(DateTime, default=datetime.datetime.utcnow)
    
class OrderSubject:
    def __init__(self, order):
        self.order = order
        self._observers = []
        
    def attach(self, observer):
        self._observers.append(observer)
    
    def set_status(self, new_status, db_session):
        old_status = self.order.status
        self.order.status = new_status
        db_session.commit()
        self.notify(old_status, new_status, db_session)
        
    def notify(self, old_status, new_status, db_session):
        for observer in self._observers:
            observer.update(self.order, old_status, new_status, db_session)
        
class OrderObserver:
    def update(self, order, old_status, new_status, db_session):
        raise NotImplementedError

#concrete observers   
class InvoiceCreator(OrderObserver):
    def update(self, order, old_status, new_status, db_session):
        if new_status == 'PENDING':
            print(f"Creating invoice for Order #{order.id}")
            
        customer_id = order.customer_id
        
        invoice = Invoice(customer_id = customer_id, order_id = order.id, email = order.email, total = order.total)
        db_session.add(invoice)
        db_session.commit()
        
#decide how to work out the receipt creator later, because don't know if we're going to use a payments table
# class ReceiptCreator(OrderObserver):
#     def update(self, order, old_status, new_status, db_session):
#         if new_status == 'IN PROCESS':
#             print(f"Creating receipt for Order #{order.id}")
        
#         customer_id = order.customer_id
        
#         receipt = Receipt(order_id = order.id, payment_id)
        
            
            
            