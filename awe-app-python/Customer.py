from Account import Account

class Customer(Account):
    def __init__(self, username, password, name, email, shipping_address, phone_number):
        super().__init__(username, password, name, email)
        self.name = name
        self.shipping_address = shipping_address
        self.phone_number = phone_number
        self.order_history = []
    
    def to_dict(self):
        data = super().to_dict()
        data["type"] = "Customer"
        data["shipping_address"] = self.shipping_address
        data["phone_number"] = self.phone_number
        return data
    
    @staticmethod
    def from_dict(data):
        return Customer(
            data["username"],
            data["password"],
            data["name"],
            data["email"],
            data["shipping_address"],
            data["phone_number"]
        )
    
    def get_order_history(self):
        return self.order_history #maybe change to spit out a list instead
    
    