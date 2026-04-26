from models.user_model import db, User

class UserService:
    def __init__(self):
        pass
        
    def add_user(self, username):
        """
        Add a new user to the database
        """
        user = User(username=username)
        db.session.add(user)
        db.session.commit()
        return user
    
    def get_user_by_name(self, username):
        """
        Get a user by username
        """
        return User.query.filter_by(username=username).first()
