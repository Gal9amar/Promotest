#!/usr/bin/env python3
import random
import string

def generate_code(length=16):
    """Generate a random code with uppercase letters and numbers"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_codes(count=10000, base_url="https://chatgpt.com/?promoCode="):
    """Generate multiple codes and format them as URLs"""
    codes = []
    for i in range(count):
        code = generate_code()
        url = f"{base_url}{code}"
        codes.append(url)
    
    return codes

def save_to_file(codes, filename="generated_codes.txt"):
    """Save the generated codes to a text file"""
    with open(filename, 'w') as f:
        for code in codes:
            f.write(code + '\n')
    print(f"Generated {len(codes)} codes and saved to {filename}")

if __name__ == "__main__":
    # Generate 10,000 codes
    print("Generating 10,000 codes...")
    codes = generate_codes(10000)
    
    # Save to file
    save_to_file(codes)
    
    # Show first 5 examples
    print("\nFirst 5 examples:")
    for i, code in enumerate(codes[:5]):
        print(f"{i+1}. {code}")
