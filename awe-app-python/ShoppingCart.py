from Product import Product
from typing import List
import random

class CartItem:
    def __init__(self, product: Product, quantity: int = 1):
        self.product = product
        self.quantity = quantity
    
    def calculate_subtotal(self):
        total = self.product.price * self.quantity
        return total
    

class ShoppingCart:
    def __init__(self):
        self.id = random.randint(1, 1000)
        self.products: List[CartItem] = []
        
    def to_dict(self):
        return{
            "id": self.id,
            "products": [item.to_dict() for item in self.products]
        }
    
    @staticmethod
    def from_dict(data):
        products_data = data.get("products", [])
        products = [CartItem.from_dict(item) for item in products_data]
        return ShoppingCart(
            id = data.get("id"),
            products = products
            
        )

    def add_product(self, product: Product, quantity: int):
        
        #check if the product is already a cart item in this cart
        for item in self.products:
            if item.product_id == product.id:
                item.quantity += quantity
            return
        
        #if not, then it's added as a cart item
        self.products.append(CartItem(product.id, quantity))
    
    def reduce_item_quantity(self, product: Product, quantity: int):
        
        for item in self.products:
            if item.product_id == product.id:
                #if the quantity of the product in the cart is greater than the amount
                #that the customer wants to reduce it by (e.g. remove one of 2 items)
                if item.quantity > quantity:
                    item.quantity -= quantity
                else:
                    self.products.remove(item)
                break
    
    def calculate_total(self):
        total = 0
        for item in self.products:
            subtotal = item.calculate_subtotal()
            total += subtotal
        return total
            
    