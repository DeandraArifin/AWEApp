from enum import Enum as PyEnum
import datetime
from sqlalchemy import Float, Column, Integer, String, Enum, ForeignKey, null, UniqueConstraint, DateTime
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()
  
class OrderStatus(PyEnum):
    PENDING = 'pending'
    IN_PROCESS = 'in process'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey('shopping_cart.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    
    cart = relationship('ShoppingCart', back_populates='items')
    product = relationship('Product')
    
    __table_args__ = (
        UniqueConstraint('cart_id', 'product_id', name='unique_cart_product'),
    )
    
    def calculate_subtotal(self) -> float:
        total = self.product.price * self.quantity
        return total
    

# class ShoppingCart:
#     __tablename__= 'shopping_carts'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
#     owner = relationship('Customer', back_populates='cart')
#     items = relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')        

#     def add_product(self, product: Product, quantity: int, session: Session):
#         #check if the product is already a cart item in this cart
#         for item in self.items:
#             if item.product_id == product.id:
#                 item.quantity += quantity
#                 session.commit()
#             return
        
#         #if not, then it's added as a cart item
#         self.products.append(CartItem(product.id, quantity))
    
#     def reduce_item_quantity(self, product: Product, quantity: int, session: Session):
        
#         for item in self.items:
#             if item.product_id == product.id:
#                 #if the quantity of the product in the cart is greater than the amount
#                 #that the customer wants to reduce it by (e.g. remove one of 2 items)
#                 if item.quantity > quantity:
#                     item.quantity -= quantity
#                 else:
#                     self.items.remove(item)
#                 session.commit()
#                 break
    
#     def calculate_total(self) -> float:
#         return sum(item.calculate_subtotal() for item in self.items)
    
#     def checkout(self, session, full_name=None, email=None, shipping_address=None, phone_number=None):
#         #checks if cart is empty
#         if not self.items:
#             raise ValueError("Cannot checkout an empty cart")
        
#         #if customer id field is empty it indicates that it's a guest user
#         if self.customer_id:
#             customer = session.query(Customer).get(self.customer_id)
#             full_name = customer.full_name
#             email = customer.email
#         elif not full_name or not email:
#             raise ValueError("Guest checkout requires full_name and email") #implement input validation in UI too
        
#         order = Order(
#             customer_id = self.customer_id,
#             full_name = full_name,
#             email = email,
#             total = self.calculate_total(),
#             status = OrderStatus.PENDING
#         )
        
#         for item in self.items:
#             order_item = OrderItem(
#                 product_id = item.product_id,
#                 quantity = item.quantity,
#                 price = item.calculate_subtotal()
#             )
#             order.items.append(order_item)
            
#         session.add(order)
#         session.commit()
#         return order

# class OrderItem(Base):
#     __tablename__ = 'order_items'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     order_id = Column(Integer, ForeignKey('orders.id', nullable=False))
#     product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
#     quantity = Column(Integer, nullable=False)
#     price = Column(Float, nullable=False)
    
#     order = relationship('Order', back_populates='items')
#     product = relationship('Product')
    
# class Order(Base):
#     __tablename__ ='orders'
    
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
#     full_name = Column(String(255), nullable=False)
#     email = Column(String(255), nullable=False)
#     shipping_address = Column(String(255), nullable=False)
#     status = Column(Enum(OrderStatus), nullable=False)
#     total = Column(Float, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
    
#     customer = relationship('Customer', back_populates='orders')
#     items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    
#     def get_total_sum(self):
#         return self.total
    
#     def set_status(self, status: OrderStatus):
#         self.status = status
    
    
    
class ProductCategory(PyEnum):
    SMARTPHONES = "Smartphones"
    LAPTOPS = "Laptops"
    TABLETS = "Tablets"
    TELEVISIONS = "Televisions"
    CAMERAS = "Cameras"
    AUDIO = "Audio"
    ACCESSORIES = "Accessories"
    
    
class Product(Base):
    
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    category = Column(Enum(ProductCategory), nullable=False)
    
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