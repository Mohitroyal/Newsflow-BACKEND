import psycopg2

db_url = "postgresql://postgres:9346843889v@db.rffrqokpnqoycpozrjuc.supabase.co:5432/postgres"
try:
    print("Connecting to Supabase PostgreSQL database...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Add font_family if it doesn't exist
    print("Adding font_family column if it doesn't exist...")
    cursor.execute("ALTER TABLE clippings ADD COLUMN IF NOT EXISTS font_family VARCHAR DEFAULT 'playfair';")
    
    conn.commit()
    print("Migration completed successfully!")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error during migration: {e}")
