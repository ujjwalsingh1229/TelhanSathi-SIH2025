import sqlite3

conn = sqlite3.connect('instance/telhan_sathi.db')
cursor = conn.cursor()

try:
    # Create buyers table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buyers (
            id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            buyer_name VARCHAR(255) NOT NULL,
            phone VARCHAR(20),
            company_name VARCHAR(255),
            location VARCHAR(255),
            district VARCHAR(100),
            state VARCHAR(100),
            is_verified BOOLEAN,
            is_active BOOLEAN,
            created_at DATETIME,
            updated_at DATETIME
        )
    ''')
    conn.commit()
    print("✅ buyers table created (or already exists)")
except sqlite3.OperationalError as e:
    print(f"❌ Error: {e}")
finally:
    conn.close()
