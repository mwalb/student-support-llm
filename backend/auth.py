"""
auth.py - Complete Authentication System
Bonus D: Authentication with User Management
"""

import os
import json
import secrets
import hashlib
from datetime import datetime
from typing import Optional, Dict
from fastapi import HTTPException, Header

# ============================================
# USER DATABASE (JSON File)
# ============================================
USER_DB_FILE = "users.json"

def load_users() -> Dict:
    """Load users from JSON file"""
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users: Dict):
    """Save users to JSON file"""
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# ============================================
# USER MANAGEMENT FUNCTIONS
# ============================================

def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_api_key() -> str:
    """Generate a unique API key"""
    return secrets.token_hex(32)

def create_user(username: str, password: str, email: str, role: str = "student") -> Dict:
    """Create a new user"""
    users = load_users()
    
    # Check if user exists
    if username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists
    for user_data in users.values():
        if user_data.get("email") == email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    api_key = generate_api_key()
    user_data = {
        "username": username,
        "password": hash_password(password),
        "email": email,
        "role": role,
        "api_key": api_key,
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }
    
    users[username] = user_data
    save_users(users)
    
    return {
        "username": username,
        "api_key": api_key,
        "role": role,
        "email": email,
        "message": "User created successfully"
    }

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """Authenticate a user"""
    users = load_users()
    
    if username not in users:
        return None
    
    user = users[username]
    if user["password"] != hash_password(password):
        return None
    
    # Update last login
    user["last_login"] = datetime.now().isoformat()
    save_users(users)
    
    return {
        "username": username,
        "api_key": user["api_key"],
        "role": user["role"],
        "email": user["email"]
    }

def validate_api_key(api_key: str) -> Optional[Dict]:
    """Validate API key and return user info"""
    users = load_users()
    
    for username, user in users.items():
        if user.get("api_key") == api_key:
            return {
                "username": username,
                "role": user.get("role", "student"),
                "email": user.get("email")
            }
    return None

def verify_api_key(api_key: str = Header(...)):
    """FastAPI dependency for API key validation"""
    user_info = validate_api_key(api_key)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user_info

def get_all_users() -> Dict:
    """Get all users (admin only)"""
    users = load_users()
    # Remove passwords for security
    for username, user in users.items():
        user.pop("password", None)
    return users

def delete_user(username: str) -> bool:
    """Delete a user"""
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        return True
    return False

def get_user_by_username(username: str) -> Optional[Dict]:
    """Get a user by username"""
    users = load_users()
    if username in users:
        user = users[username].copy()
        user.pop("password", None)
        return user
    return None
