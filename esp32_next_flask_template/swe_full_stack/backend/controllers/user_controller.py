from flask import jsonify
from services.user_service import UserService

class UserController:
    def __init__(self):
        self.user_service = UserService()
    
    def add_user(self, name):
        """
        Controller method to add a user
        """
        print(f'Adding user: {name}')
        user = self.user_service.add_user(name)
        return jsonify({"message": f"User {name} added."})
