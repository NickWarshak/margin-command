import bcrypt

# 1. Type your desired passwords in this list
passwords_to_hash = ['Njwnjw3854!!', 'Jakeis#1']

print("--- COPY THESE HASHES FOR YOUR YAML ---")

for pw in passwords_to_hash:
    # Convert string to bytes
    byte_pw = pw.encode('utf-8')
    # Generate a secure salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(byte_pw, salt)
    
    # Decode back to string for easy copying
    print(f"Plaintext: {pw}")
    print(f"Hash: {hashed.decode('utf-8')}")
    print("-" * 30)