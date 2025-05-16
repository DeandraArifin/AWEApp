from Account import Account
from Customer import Customer
from Admin import Admin
from typing import List, Optional
import os
import json

class AccountManager:
    def __init__(self, filepath="accounts.json"):
        self.accounts: List[Account] = []
        self.filepath = filepath
        self.load_from_file()
    
    def load_from_file(self):
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, "r") as f:
            data = json.load(f)
            for acc_dict in data:
                if acc_dict["type"] == "Customer":
                    self.accounts.append(Customer.from_dict(acc_dict))
                if acc_dict["type"] == "Admin":
                    self.accounts.append(Admin.from_dict(acc_dict))
                else:
                    self.accounts.append(Account.from_dict(acc_dict))
                    
    def save_to_file(self):
        with open(self.filepath, "w") as f:
            json.dump([acc.to_dict() for acc in self.accounts], f, indent=4)
    
    def add_account(self, account: Account):
        if self.account_exists(account.username):
            print(f"Username '{account.username}' already exists. Choose a different one.")
            return
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
        
        if self.account_exists(username):
            print(f"Username '{username}' already exists. Registration aborted.")
            return False
        
        new_cust_acc = Customer(username, password, name, email, shipping_address, phone_number)
        self.add_account(new_cust_acc)