"""Database initialization script - creates tables and adds sample data."""
import psycopg2
from db_config import DB_CONFIG

def init_database():
    """Initialize the database with tables and sample data"""
    conn = None
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("Creating Node table...")
        
        # Create Node table with primary key, indexed id, and indexed name
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "Node" (
                id SERIAL PRIMARY KEY,
                name VARCHAR(240) NOT NULL
            );
        """)
        
        # Create index on name field
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_node_name ON "Node"(name);
        """)
        
        print("Creating Artist table...")
        
        # Create Artist table with indexed artistId column
        # Note: PRIMARY KEY automatically creates an index
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "Artist" (
                "artistId" INTEGER PRIMARY KEY
            );
        """)
        
        # Check if table already has data
        cur.execute("SELECT COUNT(*) FROM \"Node\";")
        count = cur.fetchone()[0]
        
        if count == 0:
            print("Adding 19 random globally diverse names...")
            
            # 19 globally diverse human names
            names = [
                'Amara Okafor',      # Nigerian
                'Chen Wei',          # Chinese
                'Priya Sharma',      # Indian
                'Mohammed Al-Rashid', # Saudi Arabian
                'Sofia Rodriguez',   # Spanish
                'Yuki Tanaka',       # Japanese
                'Fatima Hassan',     # Egyptian
                'Lars Andersson',    # Swedish
                'Nadia Kozlov',      # Russian
                'Kwame Mensah',      # Ghanaian
                'Isabella Costa',    # Brazilian
                'Arjun Patel',       # Indian
                'Leila Azizi',       # Iranian
                'Diego Martinez',    # Mexican
                'Aisha Diallo',      # Senegalese
                'Kim Min-jun',       # Korean
                'Zara Abadi',        # Ethiopian
                'Rafael Santos',     # Portuguese
                'Mei Ling Wang'      # Chinese
            ]
            
            # Insert names into table
            for name in names:
                cur.execute("INSERT INTO \"Node\" (name) VALUES (%s);", (name,))
            
            print(f"Successfully added {len(names)} names to the database.")
        else:
            print(f"Table already contains {count} records. Skipping data insertion.")
        
        # Check if Artist table already has data
        cur.execute("SELECT COUNT(*) FROM \"Artist\";")
        artist_count = cur.fetchone()[0]
        
        if artist_count == 0:
            print("Adding 19 artist records...")
            
            # Insert artistId values from 1 to 19 to match Node IDs
            for artist_id in range(1, 20):
                cur.execute("INSERT INTO \"Artist\" (\"artistId\") VALUES (%s);", (artist_id,))
            
            print(f"Successfully added 19 artist records to the database.")
        else:
            print(f"Artist table already contains {artist_count} records. Skipping data insertion.")
        
        # Commit the transaction
        conn.commit()
        print("Database initialization completed successfully!")
        
        # Display the data
        cur.execute("SELECT id, name FROM \"Node\" ORDER BY id;")
        rows = cur.fetchall()
        print("\nCurrent nodes in database:")
        for row in rows:
            print(f"  ID: {row[0]}, Name: {row[1]}")
        
        # Display artist data
        cur.execute("SELECT \"artistId\" FROM \"Artist\" ORDER BY \"artistId\";")
        artist_rows = cur.fetchall()
        print("\nCurrent artists in database:")
        for row in artist_rows:
            print(f"  Artist ID: {row[0]}")
        
        cur.close()
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_database()
