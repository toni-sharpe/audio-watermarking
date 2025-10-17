"""Database configuration and connection management."""
import psycopg2
from psycopg2 import pool
import os

# Database connection parameters
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432'),
    'database': os.environ.get('DB_NAME', 'audio_watermark'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres')
}

# Connection pool
connection_pool = None

def init_connection_pool():
    """Initialize the connection pool"""
    global connection_pool
    if connection_pool is None:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,
            **DB_CONFIG
        )
    return connection_pool

def get_db_connection():
    """Get a connection from the pool"""
    if connection_pool is None:
        init_connection_pool()
    return connection_pool.getconn()

def release_db_connection(conn):
    """Return a connection to the pool"""
    if connection_pool:
        connection_pool.putconn(conn)

def close_all_connections():
    """Close all connections in the pool"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        connection_pool = None
