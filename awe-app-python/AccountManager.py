from Models import Account, Customer, Admin
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List, Optional
import os
import json

class AccountManager:
    def __init__(self, session: Session):
        self.session = session
    
    def add_account(self, account: Account):
        if self.account_exists(account.username):
            print(f"Username '{account.username}' already exists. Choose a different one.")
            return
        self.session.add(account)
        self.session.commit()
        
    def account_exists(self, username:str):
        return self.session.query(Account).filter_by(username=username).first() is not None
    
    def login(self, username:str, password:str):
        account = None
        for a in self.accounts:
            if a.username == username:
                account = a
        if(account == None):
            return None
        if(account.authenticate(username, password)):
            return account.username
        else:
            return None
        
    def register(self, username, password, name, email, shipping_address, phone_number):
        
        if self.account_exists(username):
            print(f"Username '{username}' already exists. Registration aborted.")
            return False
        
        new_cust_acc = Customer(username, password, name, email, shipping_address, phone_number)
        self.add_account(new_cust_acc)