import bcrypt

passwords_to_hash = ['Njwnjw3854!!', 'Jakeis#1']

print("--- COPY THESE HASHES FOR YOUR YAML ---")

for pw in passwords_to_hash:
    byte_pw = pw.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(byte_pw, salt)
    
    print(f"Plaintext: {pw}")
    print(f"Hash: {hashed.decode('utf-8')}")
    print("-" * 30)