"""Update ArtistCollective data to meet requirements for hierarchical display.

This script adds artists to multiple collectives to meet the requirement:
"Some artists should be in more than one collective"

Requirements met:
- One collective has no artists (Rhythmic Fusion)
- One collective has one artist (Harmonic Resonance)
- Three collectives have many artists (Melodic Synthesis, Acoustic Ensemble, Sonic Wavelength)
- Some artists are in multiple collectives (4 artists are in 2 collectives each)
"""
import psycopg2
from db_config import DB_CONFIG

def update_artist_collective_data():
    """Update artist-collective assignments to have some artists in multiple collectives"""
    conn = None
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        print("Updating artist-collective assignments...")
        
        # Get collective IDs to verify they exist
        cur.execute('SELECT "collectiveId" FROM "Collective" ORDER BY "collectiveId"')
        collectives = [row[0] for row in cur.fetchall()]
        
        if len(collectives) < 5:
            print("Error: Not enough collectives found. Run migrate_collectives.py first.")
            return
        
        print(f"Found {len(collectives)} collectives: {collectives}")
        
        # Add artists to multiple collectives
        # Note: These assignments assume the collective IDs from migrate_collectives.py:
        # 20: Harmonic Resonance (should have 1 artist)
        # 21: Rhythmic Fusion (should be empty)
        # 22: Melodic Synthesis (should have many)
        # 23: Acoustic Ensemble (should have many)
        # 24: Sonic Wavelength (should have many)
        
        multi_assignments = [
            (1, 22),   # Amara Okafor: add to Melodic Synthesis (already in Sonic Wavelength)
            (3, 24),   # Priya Sharma: add to Sonic Wavelength (already in Acoustic Ensemble)
            (5, 23),   # Sofia Rodriguez: add to Acoustic Ensemble (already in Sonic Wavelength)
            (12, 23),  # Arjun Patel: add to Acoustic Ensemble (already in Melodic Synthesis)
        ]
        
        print("\nAdding artists to multiple collectives...")
        for artist_id, collective_id in multi_assignments:
            try:
                cur.execute("""
                    INSERT INTO "ArtistCollective" ("artistId", "collectiveId")
                    VALUES (%s, %s)
                    ON CONFLICT DO NOTHING
                """, (artist_id, collective_id))
                print(f"  Added artist {artist_id} to collective {collective_id}")
            except Exception as e:
                print(f"  Failed to add artist {artist_id} to collective {collective_id}: {e}")
        
        conn.commit()
        
        # Verify the results
        print("\n" + "="*60)
        print("VERIFICATION")
        print("="*60)
        
        # Check collective distribution
        cur.execute("""
            SELECT c."collectiveId", n.name, COUNT(ac."artistId") as artist_count
            FROM "Collective" c
            JOIN "Node" n ON c."collectiveId" = n.id
            LEFT JOIN "ArtistCollective" ac ON c."collectiveId" = ac."collectiveId"
            GROUP BY c."collectiveId", n.name
            ORDER BY c."collectiveId"
        """)
        results = cur.fetchall()
        print("\nCollective distribution:")
        for row in results:
            print(f"  {row[1].strip()}: {row[2]} artists")
        
        # Check multi-collective artists
        cur.execute("""
            SELECT ac."artistId", n1.name, COUNT(DISTINCT ac."collectiveId") as collective_count
            FROM "ArtistCollective" ac
            JOIN "Node" n1 ON ac."artistId" = n1.id
            GROUP BY ac."artistId", n1.name
            HAVING COUNT(DISTINCT ac."collectiveId") > 1
            ORDER BY ac."artistId"
        """)
        multi_artists = cur.fetchall()
        print(f"\nArtists in multiple collectives: {len(multi_artists)}")
        for row in multi_artists:
            print(f"  {row[1].strip()}: {row[2]} collectives")
        
        # Total counts
        cur.execute('SELECT COUNT(*) FROM "ArtistCollective"')
        total_assignments = cur.fetchone()[0]
        cur.execute('SELECT COUNT(DISTINCT "artistId") FROM "ArtistCollective"')
        unique_artists = cur.fetchone()[0]
        
        print(f"\nTotal artist-collective assignments: {total_assignments}")
        print(f"Unique artists: {unique_artists}")
        
        cur.close()
        print("\n" + "="*60)
        print("Update completed successfully!")
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
    update_artist_collective_data()
