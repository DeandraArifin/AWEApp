from enum import Enum as PyEnum
import Float
from Account import Customer
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, null
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()

class OrderStatus(PyEnum):
    PENDING = 'pending'
    IN_PROCESS = 'in process'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'

class Order(Base):
    __tablename__ ='orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    shipping_address = Column(String(255), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False)
    total = Column(Float, nullable=False)
    
    customer = relationship('Customer', back_populates='orders')