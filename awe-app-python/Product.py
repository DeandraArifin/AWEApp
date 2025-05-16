from enum import Enum
       
class ProductCategory(Enum):
    SMARTPHONES = "Smartphones"
    LAPTOPS = "Laptops"
    TABLETS = "Tablets"
    TELEVISIONS = "Televisions"
    CAMERAS = "Cameras"
    AUDIO = "Audio"
    ACCESSORIES = "Accessories"
    
    
class Product:
    def __init__(self, id: int, name: str, desc: str, price: float, stock: int, category: ProductCategory):
        if(category is not isinstance(category, ProductCategory)):
            raise ValueError("category must be an instance of ProductCatalogue")
        
        self.id = id
        self.name = name
        self.desc = desc
        self.price = price
        self.stock = stock
        self.category = category
        
