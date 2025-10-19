"""Test suite for collective management features"""
import pytest
from db_config import get_db_connection, release_db_connection


class TestCollectiveManagement:
    """Test suite for collective management features"""
    
    def test_artist_collective_table_exists(self):
        """Test that the ArtistCollective table exists with correct structure"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'ArtistCollective'
                );
            """)
            exists = cur.fetchone()[0]
            assert exists, "ArtistCollective table should exist"
            
            # Check columns
            cur.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'ArtistCollective'
                ORDER BY ordinal_position;
            """)
            columns = cur.fetchall()
            
            assert len(columns) == 2, "Should have 2 columns"
            assert columns[0][0] == 'artistId', "First column should be 'artistId'"
            assert columns[0][1] == 'integer', "artistId should be integer"
            assert columns[1][0] == 'collectiveId', "Second column should be 'collectiveId'"
            assert columns[1][1] == 'integer', "collectiveId should be integer"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_artist_collective_indexes(self):
        """Test that the ArtistCollective table has the required indexes"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check indexes
            cur.execute("""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'ArtistCollective'
                ORDER BY indexname;
            """)
            indexes = cur.fetchall()
            
            # Should have 3 indexes: composite primary key and 2 individual indexes
            assert len(indexes) >= 3, "Should have at least 3 indexes"
            
            index_names = [idx[0] for idx in indexes]
            assert 'ArtistCollective_pkey' in index_names, "Should have primary key index"
            assert 'idx_artistcollective_artistid' in index_names, "Should have artistId index"
            assert 'idx_artistcollective_collectiveid' in index_names, "Should have collectiveId index"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_collective_table_exists(self):
        """Test that the Collective table exists with correct structure"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'Collective'
                );
            """)
            exists = cur.fetchone()[0]
            assert exists, "Collective table should exist"
            
            # Check columns
            cur.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'Collective'
                ORDER BY ordinal_position;
            """)
            columns = cur.fetchall()
            
            assert len(columns) == 1, "Should have 1 column"
            assert columns[0][0] == 'collectiveId', "First column should be 'collectiveId'"
            assert columns[0][1] == 'integer', "collectiveId should be integer"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_collective_indexes(self):
        """Test that the Collective table has the required indexes"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check indexes
            cur.execute("""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'Collective'
                ORDER BY indexname;
            """)
            indexes = cur.fetchall()
            
            # Should have at least 1 index: primary key (which automatically creates an index)
            assert len(indexes) >= 1, "Should have at least 1 index"
            
            index_names = [idx[0] for idx in indexes]
            assert 'Collective_pkey' in index_names, "Should have primary key index"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_node_type_column_exists(self):
        """Test that the node table has nodeType column"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check if column exists
            cur.execute("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'node' AND column_name = 'nodeType';
            """)
            column = cur.fetchone()
            
            assert column is not None, "nodeType column should exist"
            assert column[1] == 'character varying', "nodeType should be varchar"
            assert column[2] == 32, "nodeType should be varchar(32)"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_artists_have_node_type(self):
        """Test that existing 19 artists have nodeType set to 'artist'"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check that first 19 records are artists
            cur.execute("""
                SELECT COUNT(*) 
                FROM node 
                WHERE id <= 19 AND "nodeType" = 'artist';
            """)
            count = cur.fetchone()[0]
            assert count == 19, f"Should have 19 artists, found {count}"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_collectives_in_node_table(self):
        """Test that 5 collectives were added to node table"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check collective count
            cur.execute("""
                SELECT COUNT(*) 
                FROM node 
                WHERE "nodeType" = 'collective';
            """)
            count = cur.fetchone()[0]
            assert count == 5, f"Should have 5 collectives, found {count}"
            
            # Check that they have valid names
            cur.execute("""
                SELECT id, name 
                FROM node 
                WHERE "nodeType" = 'collective'
                ORDER BY id;
            """)
            collectives = cur.fetchall()
            
            for collective in collectives:
                assert collective[0] > 19, "Collective IDs should be greater than 19"
                assert collective[1] is not None, "Collective name should not be None"
                assert len(collective[1]) > 0, "Collective name should not be empty"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_collectives_in_collective_table(self):
        """Test that 5 collectives were added to Collective table"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check record count
            cur.execute('SELECT COUNT(*) FROM "Collective";')
            count = cur.fetchone()[0]
            assert count == 5, f"Should have 5 collectives, found {count}"
            
            # Check that collective IDs match node IDs
            cur.execute("""
                SELECT c."collectiveId", n.id
                FROM "Collective" c
                JOIN node n ON c."collectiveId" = n.id
                WHERE n."nodeType" = 'collective'
                ORDER BY c."collectiveId";
            """)
            rows = cur.fetchall()
            
            assert len(rows) == 5, "Should have 5 matching records"
            for row in rows:
                assert row[0] == row[1], f"Collective ID {row[0]} should match Node ID {row[1]}"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_artist_collective_assignments(self):
        """Test that 19 artists are assigned to collectives"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check assignment count
            cur.execute('SELECT COUNT(*) FROM "ArtistCollective";')
            count = cur.fetchone()[0]
            assert count == 19, f"Should have 19 artist assignments, found {count}"
            
            # Check that all artists (1-19) are assigned
            cur.execute("""
                SELECT COUNT(DISTINCT "artistId") 
                FROM "ArtistCollective";
            """)
            unique_artists = cur.fetchone()[0]
            assert unique_artists == 19, f"Should have 19 unique artists assigned, found {unique_artists}"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_single_artist_in_collective(self):
        """Test that one collective has only one artist"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Find collectives with single artist
            cur.execute("""
                SELECT "collectiveId", COUNT("artistId") as artist_count
                FROM "ArtistCollective"
                GROUP BY "collectiveId"
                HAVING COUNT("artistId") = 1;
            """)
            single_collectives = cur.fetchall()
            
            assert len(single_collectives) == 1, "Should have exactly 1 collective with single artist"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_empty_collective(self):
        """Test that one collective is empty"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Find empty collectives
            cur.execute("""
                SELECT c."collectiveId"
                FROM "Collective" c
                WHERE c."collectiveId" NOT IN (
                    SELECT DISTINCT "collectiveId" FROM "ArtistCollective"
                );
            """)
            empty_collectives = cur.fetchall()
            
            assert len(empty_collectives) == 1, "Should have exactly 1 empty collective"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_api_artists_endpoint(self):
        """Test that the /api/artists endpoint returns artists with collectives"""
        from app import app
        import json
        
        with app.test_client() as client:
            response = client.get('/api/artists')
            
            assert response.status_code == 200, "API should return 200"
            
            data = json.loads(response.data)
            assert len(data) == 19, f"Should return 19 artists, got {len(data)}"
            
            # Check that artists have the expected fields
            for artist in data:
                assert 'id' in artist, "Artist should have id field"
                assert 'name' in artist, "Artist should have name field"
                assert 'collective' in artist, "Artist should have collective field"
                assert 'collectiveId' in artist, "Artist should have collectiveId field"
            
            # Check that at least one artist has a collective
            artists_with_collective = [a for a in data if a['collective'] is not None]
            assert len(artists_with_collective) >= 18, "At least 18 artists should have collectives"
