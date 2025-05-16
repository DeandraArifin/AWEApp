class Account:
    def __init__(self, username: str, password: str, full_name:str, email:str):
        self.username = username
        self._password = password #follow python conventions of protected attributes
        self.full_name = full_name
        self.email = email
    
    def authenticate(self, username: str, password:str):
        return self.username == username and self._password == password
    
    def get_email(self):
        return self.email
    
    def get_name(self):
        return self.full_name
        