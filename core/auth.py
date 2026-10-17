import hashlib
import secrets
from core.db import get_user_by_name, create_user, update_user_password, get_user

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a unique salt."""
    if not password:
        return ""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${key.hex()}"

def verify_password(stored_hash: str | None, password: str) -> bool:
    """Verify a plain password against a stored PBKDF2 salt$hash string."""
    if not stored_hash or not password:
        return False
    try:
        parts = stored_hash.split("$", 1)
        if len(parts) != 2:
            return False
        salt, key_hex = parts
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
        return secrets.compare_digest(key.hex(), key_hex)
    except Exception:
        return False

def authenticate(username: str, password: str = ""):
    """
    Authenticate a user by username and password.
    Supports legacy users without passwords seamlessly.
    Returns:
        (user_dict, None) on success
        (None, error_message) on failure
    """
    username = (username or "").strip()
    if not username:
        return None, "Please enter your username or reader name."

    user = get_user_by_name(username)
    if not user:
        return None, f"No reader found with name '{username}'. Check your spelling or sign up below."

    stored_hash = user.get("password_hash")

    # If this is a legacy account that has no password yet:
    if not stored_hash:
        if password:
            # Set this password for future logins
            new_hash = hash_password(password)
            update_user_password(user["id"], new_hash)
            user["password_hash"] = new_hash
        return user, None

    if not password:
        return None, "Please enter your password."

    if not verify_password(stored_hash, password):
        return None, "Incorrect password. Please try again."

    return user, None

def register_user(name: str, password: str, persona: str, interests: list[str], avoid: list[str]):
    """
    Register a new user profile with password and curated interests.
    Returns:
        (user_dict, None) on success
        (None, error_message) on failure
    """
    name = (name or "").strip()
    if not name:
        return None, "Please enter your name or username."
    if len(name) < 2:
        return None, "Name must be at least 2 characters long."
    if not password:
        return None, "Please choose a password."
    if len(password) < 4:
        return None, "Password must be at least 4 characters long."
    if not interests or len(interests) < 2:
        return None, "Please select at least 2 topics of interest."

    existing = get_user_by_name(name)
    if existing:
        return None, f"An account with the name '{name}' already exists. Please log in or choose a different name."

    pwd_hash = hash_password(password)
    uid = create_user(name, persona, interests, avoid, password_hash=pwd_hash)
    user = get_user(uid)
    return user, None
