# from Account import Account
import enum
from Models import AccountType
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, null
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()
class AccountType(Enum):
    CUSTOMER = 'customer'
    ADMIN = 'admin'

class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    
    __mapper_args__ = {
        'polymorphic_on' : account_type,
        'polymorphic_identity' : 'account'
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
    #cart
    orders = relationship('Order', back_populates='customer')
    
    __mapper_args__ = {
        'polymorphic_identity': 'customer'
    }
    
    
    def get_order_history(self):
        return list(self.orders) #maybe change to spit out a list instead
    
class Admin(Account):
    
    __tablename__ = 'admins'
    
    id = Column(Integer, ForeignKey('accounts.id'), primary_key=True)
    employee_id = Column(Integer, nullable=False, unique=True)
    
    #maybe define a getter function for employee id?