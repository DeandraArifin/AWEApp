from Account import Account
from Customer import Customer
from typing import List, Optional

class AccountManager:
    def __init__(self):
        self.accounts: List[Account] = []
    
    def add_account(self, account: Account):
        self.accounts.append(account)
        
    def account_exists(self, username:str):
        
        for account in self.accounts:
            
            if account.username == username:
                return True
            
        return False
    
    def login(self, username:str, password:str):
        account = None
        for a in self.accounts:
            if a.username == username:
                account = a
        
        if(account.authenticate(username, password)):
            return account.username
        else:
            return None
        
    def register(self, username, password, name, email, shipping_address, phone_number):
        new_cust_acc = Customer(username, password, name, email, shipping_address, phone_number)
        self.add_account(new_cust_acc)