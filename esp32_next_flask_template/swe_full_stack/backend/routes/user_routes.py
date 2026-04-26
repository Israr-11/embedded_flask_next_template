from flask import Blueprint
from controllers.user_controller import UserController

user_bp = Blueprint('user', __name__)
user_controller = UserController()

@user_bp.route('/add_user/<name>')
def add_user(name):
    return user_controller.add_user(name)
