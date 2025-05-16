from Account import Account

class Customer(Account):
    def __init__(self, username, password, name, email, shipping_address, phone_number):
        super().__init__(username, password, name, email)
        self.name = name
        self.shipping_address = shipping_address
        self.phone_number = phone_number
        self.order_history = []
        
    def get_order_history(self):
        return self.order_history #maybe change to spit out a list instead
    
    