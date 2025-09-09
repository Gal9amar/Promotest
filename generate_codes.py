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
    # Generate N codes and save only
    total_to_generate = 10000
    print(f"Generating {total_to_generate} codes...")
    codes = generate_codes(total_to_generate)
    save_to_file(codes)
    print("Done. See generated_codes.txt")
    
    # Show HTML table with clickable URLs
    print("\nCreating HTML table...")
    try:
        from show_urls_table import create_html_table, open_in_browser
        html_file = create_html_table()
        if html_file:
            open_in_browser(html_file)
            print("HTML table opened in browser!")
    except ImportError:
        print("Run 'python show_urls_table.py' to view URLs in HTML table")
    except Exception as e:
        print(f"Error creating HTML table: {e}")
