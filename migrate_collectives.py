"""Database migration script for collective management features."""
import psycopg2
import random
from db_config import DB_CONFIG

def migrate_database():
    """Migrate the database to add collective management features"""
    conn = None
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Task 1: Create ArtistCollective link table
        print("Task 1: Creating ArtistCollective link table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "ArtistCollective" (
                "artistId" INTEGER NOT NULL,
                "collectiveId" INTEGER NOT NULL,
                PRIMARY KEY ("artistId", "collectiveId")
            );
        """)
        
        # Create indexes on both columns
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_artistcollective_artistid 
            ON "ArtistCollective"("artistId");
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_artistcollective_collectiveid 
            ON "ArtistCollective"("collectiveId");
        """)
        conn.commit()
        print("✓ ArtistCollective table created with indexes")
        
        # Task 2: Create Collective table
        print("\nTask 2: Creating Collective table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS "Collective" (
                "collectiveId" INTEGER PRIMARY KEY
            );
        """)
        conn.commit()
        print("✓ Collective table created")
        
        # Task 3: Add nodeType column to Node table
        print("\nTask 3: Adding nodeType column to Node table...")
        # Check if column already exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'Node' AND column_name = 'nodeType';
        """)
        if cur.fetchone() is None:
            cur.execute("""
                ALTER TABLE "Node" 
                ADD COLUMN "nodeType" VARCHAR(32);
            """)
            
            # Set existing 19 artists to "artist"
            cur.execute("""
                UPDATE "Node" 
                SET "nodeType" = 'artist' 
                WHERE id <= 19;
            """)
            conn.commit()
            print("✓ nodeType column added and existing artists updated")
        else:
            print("✓ nodeType column already exists")
        
        # Task 4: Add 5 collectives to Node table
        print("\nTask 4: Adding 5 collectives to Node table...")
        
        # Check if collectives already exist
        cur.execute("""
            SELECT COUNT(*) FROM "Node" WHERE "nodeType" = 'collective';
        """)
        collective_count = cur.fetchone()[0]
        
        if collective_count < 5:
            # Creative collective names using musical terms
            collective_names = [
                'Harmonic Resonance',
                'Rhythmic Fusion',
                'Melodic Synthesis',
                'Acoustic Ensemble',
                'Sonic Wavelength'
            ]
            
            for name in collective_names:
                cur.execute("""
                    INSERT INTO "Node" (name, "nodeType") 
                    VALUES (%s, 'collective');
                """, (name,))
            
            conn.commit()
            print(f"✓ Added {len(collective_names)} collectives to Node table")
        else:
            print(f"✓ {collective_count} collectives already exist")
        
        # Task 5: Add collectives to Collective table
        print("\nTask 5: Adding collectives to Collective table...")
        
        # Get collective IDs from Node table
        cur.execute("""
            SELECT id FROM "Node" WHERE "nodeType" = 'collective' ORDER BY id;
        """)
        collective_ids = [row[0] for row in cur.fetchall()]
        
        # Check if collectives already in Collective table
        cur.execute('SELECT COUNT(*) FROM "Collective";')
        existing_count = cur.fetchone()[0]
        
        if existing_count == 0:
            for collective_id in collective_ids:
                cur.execute("""
                    INSERT INTO "Collective" ("collectiveId") 
                    VALUES (%s);
                """, (collective_id,))
            
            conn.commit()
            print(f"✓ Added {len(collective_ids)} collectives to Collective table")
        else:
            print(f"✓ {existing_count} collectives already in Collective table")
        
        # Task 6: Assign artists to collectives
        print("\nTask 6: Assigning artists to collectives...")
        
        # Check if assignments already exist
        cur.execute('SELECT COUNT(*) FROM "ArtistCollective";')
        assignment_count = cur.fetchone()[0]
        
        if assignment_count == 0:
            # Get all artist IDs (1-19)
            artist_ids = list(range(1, 20))
            
            # Shuffle to randomize
            random.shuffle(artist_ids)
            
            # Make one artist single (assign to collective alone)
            single_artist = artist_ids[0]
            single_collective = collective_ids[0]
            
            # Leave one collective empty
            empty_collective = collective_ids[1]
            
            # Assign the single artist
            cur.execute("""
                INSERT INTO "ArtistCollective" ("artistId", "collectiveId") 
                VALUES (%s, %s);
            """, (single_artist, single_collective))
            
            # Assign remaining 18 artists to the other 3 collectives
            remaining_artists = artist_ids[1:]
            available_collectives = [c for c in collective_ids if c not in [single_collective, empty_collective]]
            
            # Distribute remaining artists randomly
            for artist_id in remaining_artists:
                collective_id = random.choice(available_collectives)
                cur.execute("""
                    INSERT INTO "ArtistCollective" ("artistId", "collectiveId") 
                    VALUES (%s, %s);
                """, (artist_id, collective_id))
            
            conn.commit()
            print(f"✓ Assigned 19 artists to collectives")
            print(f"  - Artist {single_artist} is alone in collective {single_collective}")
            print(f"  - Collective {empty_collective} is empty")
        else:
            print(f"✓ {assignment_count} artist assignments already exist")
        
        # Display summary
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        
        # Show all nodes with their types
        cur.execute('SELECT id, name, "nodeType" FROM "Node" ORDER BY id;')
        nodes = cur.fetchall()
        print(f"\nTotal nodes: {len(nodes)}")
        print("\nArtists:")
        for node in nodes:
            if node[2] == 'artist':
                print(f"  ID {node[0]}: {node[1]}")
        
        print("\nCollectives:")
        for node in nodes:
            if node[2] == 'collective':
                print(f"  ID {node[0]}: {node[1]}")
        
        # Show artist assignments
        print("\nArtist-Collective Assignments:")
        cur.execute("""
            SELECT ac."artistId", n1.name, ac."collectiveId", n2.name
            FROM "ArtistCollective" ac
            JOIN "Node" n1 ON ac."artistId" = n1.id
            JOIN "Node" n2 ON ac."collectiveId" = n2.id
            ORDER BY ac."collectiveId", ac."artistId";
        """)
        assignments = cur.fetchall()
        
        current_collective = None
        for assignment in assignments:
            if assignment[2] != current_collective:
                current_collective = assignment[2]
                print(f"\n  Collective '{assignment[3]}' (ID {assignment[2]}):")
            print(f"    - {assignment[1]} (ID {assignment[0]})")
        
        # Show empty collectives
        cur.execute("""
            SELECT c."collectiveId", n.name
            FROM "Collective" c
            JOIN "Node" n ON c."collectiveId" = n.id
            WHERE c."collectiveId" NOT IN (
                SELECT DISTINCT "collectiveId" FROM "ArtistCollective"
            );
        """)
        empty_collectives = cur.fetchall()
        if empty_collectives:
            print("\nEmpty Collectives:")
            for collective in empty_collectives:
                print(f"  - {collective[1]} (ID {collective[0]})")
        
        cur.close()
        print("\n" + "="*60)
        print("Migration completed successfully!")
        print("="*60)
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    migrate_database()
