import sqlite3

conn = sqlite3.connect('instance/telhan_sathi.db')
cursor = conn.cursor()

# First check if buyer_offers table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='buyer_offers'")
if not cursor.fetchone():
    print("❌ buyer_offers table does not exist")
    conn.close()
else:
    try:
        cursor.execute("ALTER TABLE buyer_offers ADD COLUMN buyer_id VARCHAR(36)")
        conn.commit()
        print("✅ Added buyer_id column to buyer_offers table")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e):
            print("✅ buyer_id column already exists")
        else:
            print(f"❌ Error: {e}")
    finally:
        conn.close()
