from Account import Account
from ShoppingCart import ShoppingCart

class Customer(Account):
    def __init__(self, username, password, name, email, shipping_address, phone_number, order_history=None):
        super().__init__(username, password, name, email)
        self.name = name
        self.shipping_address = shipping_address
        self.phone_number = phone_number
        self.order_history = order_history if order_history else [] #so that it returns none instead of an empty list
        self.cart = ShoppingCart()
    
    def to_dict(self):
        data = super().to_dict()
        data["type"] = "Customer"
        data["shipping_address"] = self.shipping_address
        data["phone_number"] = self.phone_number
        data["order_history"] = self.order_history
        data["cart"] = self.cart.to_dict()
        return data
    
    @staticmethod
    def from_dict(data):
        cart = ShoppingCart.from_dict(data.get("cart", {})) #restore customer cart
        order_history = data.get("order_history", [])
        return Customer(
            data["username"],
            data["password"],
            data["name"],
            data["email"],
            data["shipping_address"],
            data["phone_number"],
            cart = cart,
            order_history=order_history
        )
    
    def get_order_history(self):
        return list(self.order_history) #maybe change to spit out a list instead
    
    