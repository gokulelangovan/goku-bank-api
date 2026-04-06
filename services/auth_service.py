from services.security import hash_password
from repositories.user_repository import UserRepository
from services.jwt_handler import create_access_token
from services.security import verify_password

class AuthService:
    
    def __init__(self):
        self.user_repo = UserRepository()
        
    def register_user(self, email, password):
        
        existing_user = self.user_repo.get_user_by_email(email)
        
        if existing_user:
            raise ValueError("User already exists!!!")
            
        hashed_password = hash_password(password)
        
        user_id = self.user_repo.create_user(email, hashed_password)
        
        return user_id
        
    def login_user(self, email, password):
        
        user = self.user_repo.get_user_by_email(email)
        
        if not user:
            raise ValueError("Invalid credentials")
            
        if not verify_password(password, user["hashed_password"]):
            raise ValueError("Invalid Credentials")
            
        token = create_access_token({"user_id": user["id"]})
        
        return token
        
