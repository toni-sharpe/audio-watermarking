# Quick Reference - PostgreSQL Database Features

## Quick Start

```bash
# 1. Setup PostgreSQL database
createdb audio_watermark

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database with sample data
python init_db.py

# 4. Start the application
python app.py

# 5. Access the application
# Main page: http://127.0.0.1:5000/
# Artists page: http://127.0.0.1:5000/artists
# API endpoint: http://127.0.0.1:5000/api/nodes
```

## Database Access

### Command Line
```bash
# Connect to database
psql -U postgres -d audio_watermark -h localhost -p 5432

# View all nodes
psql -U postgres -d audio_watermark -c "SELECT * FROM node;"

# Count nodes
psql -U postgres -d audio_watermark -c "SELECT COUNT(*) FROM node;"
```

### Python Code
```python
from db_config import get_db_connection, release_db_connection

conn = get_db_connection()
try:
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM node;")
    rows = cur.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}")
    cur.close()
finally:
    release_db_connection(conn)
```

## API Endpoints

### GET /api/nodes
Returns JSON array of all nodes.

**Response:**
```json
[
  {"id": 1, "name": "Amara Okafor"},
  {"id": 2, "name": "Chen Wei"},
  ...
]
```

**Example:**
```bash
curl http://127.0.0.1:5000/api/nodes
```

## Database Schema

### Node Table
| Column | Type | Constraints | Indexed |
|--------|------|-------------|---------|
| id | SERIAL | PRIMARY KEY | Yes |
| name | CHAR(240) | NOT NULL | Yes |

## Configuration

Set environment variables to customize database connection:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=audio_watermark
export DB_USER=postgres
export DB_PASSWORD=postgres
```

## Testing

```bash
# Run all tests
pytest -v

# Run specific test files
pytest test_database.py -v
pytest test_api.py -v
pytest test_watermark.py -v
```

## Troubleshooting

**Database connection errors:**
- Ensure PostgreSQL is running: `sudo service postgresql start`
- Verify database exists: `psql -U postgres -l | grep audio_watermark`
- Check connection settings in environment variables

**API returns empty array:**
- Run `python init_db.py` to populate data
- Verify data in database: `psql -U postgres -d audio_watermark -c "SELECT COUNT(*) FROM node;"`

**Port already in use:**
- Change Flask port in `app.py`: `app.run(port=5001)`
- Or kill process using port 5000: `lsof -ti:5000 | xargs kill`
