from Models import Account, Customer, Admin
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List, Optional
from Models import AccountType

class AccountManager:
    def __init__(self, session: Session):
        self.session = session
    
    def add_account(self, account: Account):
        if self.account_exists(account.username):
            print(f"Username '{account.username}' already exists. Choose a different one.")
            return False
        self.session.add(account)
        self.session.commit()
        return True
        
    def account_exists(self, username:str):
        return self.session.query(Account).filter_by(username=username).first() is not None
    
    def login(self, username:str, password:str):
        
        account = self.session.query(Account).filter_by(username=username).first()
        
        if account and check_password_hash(account.password_hash, password):
            return account
        
        return None
        
    def register(self, username, password, name, email, shipping_address, phone_number):
        
        if self.account_exists(username):
            print(f"Username '{username}' already exists. Registration aborted.")
            return False
        
        password_hash = generate_password_hash(password)
        new_cust_acc = Customer(username, password_hash, name, email, AccountType.CUSTOMER, shipping_address, phone_number)
        
        self.add_account(new_cust_acc)
        return True