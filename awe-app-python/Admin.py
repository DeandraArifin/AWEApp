from inspect import AGEN_CLOSED


class Admin:
    name = ""
    employee_id = 0

    def __init__(self, name, employee_id):
        self.name = name
        self.employee_id = employee_id
        
    def get_name(self):
        return self.name
    