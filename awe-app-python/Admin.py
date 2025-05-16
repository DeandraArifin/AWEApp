from inspect import AGEN_CLOSED
from Account import Account

class Admin(Account):
    
    def __init__(self, username, password, name, email, employee_id):
        super().__init__(username, password, name, email, employee_id)
        self.employee_id = employee_id
        
    def to_dict(self):
        data = super().to_dict()
        data["employee_id"] = self.employee_id
        return data
    
    @staticmethod
    def from_dict(data):
        return Admin(
            data["username"],
            data["password"],
            data["name"],
            data["email"],
            data["employee_id"]
        )
        
    def get_name(self):
        return self.name
    