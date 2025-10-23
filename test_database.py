import pytest
from db_config import get_db_connection, release_db_connection


class TestDatabaseFunctions:
    """Test suite for database functions"""
    
    def test_database_connection(self):
        """Test that we can connect to the database"""
        conn = None
        try:
            conn = get_db_connection()
            assert conn is not None, "Connection should not be None"
            
            # Test that we can execute a query
            cur = conn.cursor()
            cur.execute("SELECT 1;")
            result = cur.fetchone()
            assert result[0] == 1, "Query should return 1"
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_node_table_exists(self):
        """Test that the Node table exists with correct structure"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'Node'
                );
            """)
            exists = cur.fetchone()[0]
            assert exists, "Node table should exist"
            
            # Check columns
            cur.execute("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'Node'
                ORDER BY ordinal_position;
            """)
            columns = cur.fetchall()
            
            assert len(columns) >= 2, "Should have at least 2 columns"
            assert columns[0][0] == 'id', "First column should be 'id'"
            assert columns[0][1] == 'integer', "id should be integer"
            assert columns[1][0] == 'name', "Second column should be 'name'"
            assert columns[1][1] == 'character', "name should be char"
            assert columns[1][2] == 240, "name should be char(240)"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_node_indexes(self):
        """Test that the Node table has the required indexes"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check indexes
            cur.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'Node'
                ORDER BY indexname;
            """)
            indexes = cur.fetchall()
            
            # Should have at least 2 indexes: primary key and name index
            assert len(indexes) >= 2, "Should have at least 2 indexes"
            
            index_names = [idx[0] for idx in indexes]
            assert 'Node_pkey' in index_names, "Should have primary key index"
            assert 'idx_node_name' in index_names, "Should have name index"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_node_data(self):
        """Test that the Node table has at least 19 artist records"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check record count for artists specifically
            cur.execute("SELECT COUNT(*) FROM \"Node\" WHERE \"nodeType\" = 'artist';")
            count = cur.fetchone()[0]
            assert count >= 19, f"Should have at least 19 artist records, found {count}"
            
            # Check that all records have valid data
            cur.execute("SELECT id, name FROM \"Node\" ORDER BY id;")
            rows = cur.fetchall()
            
            for row in rows:
                assert row[0] > 0, "ID should be positive"
                assert row[1] is not None, "Name should not be None"
                assert len(row[1]) > 0, "Name should not be empty"
                assert len(row[1]) <= 240, "Name should not exceed 240 characters"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_node_data_diversity(self):
        """Test that the Node data contains diverse names"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Get all names
            cur.execute("SELECT name FROM \"Node\";")
            names = [row[0] for row in cur.fetchall()]
            
            # Check for some expected names from different cultures
            assert 'Amara Okafor' in names, "Should contain Nigerian name"
            assert 'Chen Wei' in names, "Should contain Chinese name"
            assert 'Priya Sharma' in names, "Should contain Indian name"
            assert 'Mohammed Al-Rashid' in names, "Should contain Saudi Arabian name"
            assert 'Yuki Tanaka' in names, "Should contain Japanese name"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_artist_table_exists(self):
        """Test that the Artist table exists with correct structure"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'Artist'
                );
            """)
            exists = cur.fetchone()[0]
            assert exists, "Artist table should exist"
            
            # Check columns
            cur.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'Artist'
                ORDER BY ordinal_position;
            """)
            columns = cur.fetchall()
            
            assert len(columns) == 1, "Should have 1 column"
            assert columns[0][0] == 'artistId', "First column should be 'artistId'"
            assert columns[0][1] == 'integer', "artistId should be integer"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_artist_indexes(self):
        """Test that the Artist table has the required indexes"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check indexes
            cur.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = 'Artist'
                ORDER BY indexname;
            """)
            indexes = cur.fetchall()
            
            # Should have at least 1 index: primary key (which automatically creates an index)
            assert len(indexes) >= 1, "Should have at least 1 index"
            
            index_names = [idx[0] for idx in indexes]
            assert 'Artist_pkey' in index_names, "Should have primary key index"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_artist_data(self):
        """Test that the Artist table has 19 records matching Node IDs"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check record count
            cur.execute("SELECT COUNT(*) FROM \"Artist\";")
            count = cur.fetchone()[0]
            assert count == 19, f"Should have 19 records, found {count}"
            
            # Check that all artistIds are from 1 to 19
            cur.execute("SELECT \"artistId\" FROM \"Artist\" ORDER BY \"artistId\";")
            artist_ids = [row[0] for row in cur.fetchall()]
            expected_ids = list(range(1, 20))
            assert artist_ids == expected_ids, f"Artist IDs should be 1-19, got {artist_ids}"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
    
    def test_artist_node_relationship(self):
        """Test that artist IDs match Node IDs"""
        conn = None
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Check that all artist IDs have corresponding Node IDs
            cur.execute("""
                SELECT a."artistId", n.id 
                FROM "Artist" a
                LEFT JOIN "Node" n ON a."artistId" = n.id
                ORDER BY a."artistId";
            """)
            rows = cur.fetchall()
            
            # All 19 records should have matching node IDs
            assert len(rows) == 19, "Should have 19 matching records"
            
            for row in rows:
                assert row[0] == row[1], f"Artist ID {row[0]} should match Node ID {row[1]}"
            
            cur.close()
        finally:
            if conn:
                release_db_connection(conn)
