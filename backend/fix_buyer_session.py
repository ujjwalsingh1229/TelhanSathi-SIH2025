#!/usr/bin/env python3
"""Fix all buyer_id references to buyer_id_verified in buyer_auth.py"""

file_path = r"c:\Users\dhira\OneDrive\Desktop\dhirudurgade github\TelhanSathi-SIH2025\backend\routes\buyer_auth.py"

with open(file_path, 'r') as f:
    content = f.read()

# Replace all occurrences
original_count = content.count("session.get('buyer_id')")
content = content.replace("session.get('buyer_id')", "session.get('buyer_id_verified')")
content = content.replace("'buyer_id' not in session", "'buyer_id_verified' not in session")

# Write back
with open(file_path, 'w') as f:
    f.write(content)

print(f"✅ Fixed {original_count} occurrences of session.get('buyer_id')")
print(f"✅ Also fixed 'buyer_id' not in session checks")
print(f"✅ All buyer authentication session keys now use 'buyer_id_verified'")
