import secrets
import base64
import os
#Use to generate encryption keys
def generate_secret_key():
    return secrets.token_hex(16)

def generate_encryption_key():
    return base64.urlsafe_b64encode(os.urandom(32)).decode()

if __name__ == "__main__":
    secret_key = generate_secret_key()
    encryption_key = generate_encryption_key()
    
    print("Add these to your .env file:")
    print(f"SECRET_KEY={secret_key}")
    print(f"ENCRYPTION_KEY={encryption_key}")