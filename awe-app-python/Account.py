class Account:
    def __init__(self, username: str, password: str, full_name:str, email:str):
        self.username = username
        self._password = password #follow python conventions of protected attributes
        self.full_name = full_name
        self.email = email
    
    def to_dict(self):
        return {
            "type": "Account",
            "username": self.username,
            "password": self.password,
            "name": self.name,
            "email": self.email
        }
    
    @staticmethod
    def from_dict(data):
        return Account(
            data["username"],
            data["password"],
            data["name"],
            data["email"]
        )
    
    def authenticate(self, username: str, password:str):
        return self.username == username and self._password == password
    
    def get_email(self):
        return self.email
    
    def get_name(self):
        return self.full_name
        