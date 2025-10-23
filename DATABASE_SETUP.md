# Database Setup Instructions

This guide will help you set up PostgreSQL for the audio watermarking application.

## Prerequisites

- PostgreSQL installed on your system
- Python 3.x with pip

## Installation Steps

### 1. Install PostgreSQL

#### On Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### On macOS:
```bash
brew install postgresql
brew services start postgresql
```

#### On Windows:
Download and install from: https://www.postgresql.org/download/windows/

### 2. Set PostgreSQL Password and Create Database

After installing PostgreSQL, set the postgres user password and create the database:

```bash
# Switch to postgres user (Linux/Mac)
sudo -u postgres psql
```

In the PostgreSQL prompt:
```sql
-- Set the postgres user password (required for PGAdmin 4 and remote connections)
ALTER USER postgres WITH PASSWORD 'postgres';

-- Create the database
CREATE DATABASE audio_watermark;

-- Exit
\q
```

Alternatively, you can run these commands directly:
```bash
# Set password
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"

# Create database
sudo -u postgres psql -c "CREATE DATABASE audio_watermark;"
```

### 3. Configure Environment Variables (Optional)

You can customize database connection parameters by setting environment variables:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=audio_watermark
export DB_USER=postgres
export DB_PASSWORD=postgres
```

Or create a `.env` file in the project root:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=audio_watermark
DB_USER=postgres
DB_PASSWORD=postgres
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Initialize the Database

Run the initialization script to create tables and populate with sample data:

```bash
python init_db.py
```

This will:
- Create the `node` table with:
  - `id`: Auto-incrementing primary key (indexed)
  - `name`: CHAR(240) field (indexed)
- Insert 19 globally diverse human names

### 6. Verify Database Setup

Connect to PostgreSQL and verify the data:

```bash
psql -U postgres -d audio_watermark
```

In PostgreSQL prompt:
```sql
-- View the table structure
\d node

-- View the data
SELECT * FROM node;

-- View indexes
\d+ node
```

## Connecting via Command Line

### Connect to database at default port (5432):
```bash
psql -U postgres -d audio_watermark -h localhost -p 5432
```

### Common PostgreSQL Commands:
```sql
-- List all databases
\l

-- List all tables
\dt

-- Describe table structure
\d node

-- View all records
SELECT * FROM node;

-- Count records
SELECT COUNT(*) FROM node;

-- Exit
\q
```

## Connecting via PGAdmin 4

PGAdmin 4 is a popular GUI tool for managing PostgreSQL databases. Here's how to connect:

### 1. Ensure PostgreSQL Password is Set

Make sure the postgres user has the password 'postgres' (as configured in `db_config.py`):

```bash
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
```

### 2. Create a New Server Connection in PGAdmin 4

1. Open PGAdmin 4
2. Right-click on "Servers" → "Register" → "Server"
3. In the "General" tab:
   - **Name**: Audio Watermark DB (or any name you prefer)
4. In the "Connection" tab:
   - **Host name/address**: `127.0.0.1` (use IP, not "localhost")
   - **Port**: `5432`
   - **Maintenance database**: `postgres`
   - **Username**: `postgres`
   - **Password**: `postgres`
   - **Save password**: Check this box (optional)
5. Click "Save"

### 3. Navigate to the Database

After connecting:
1. Expand the server node
2. Expand "Databases"
3. Find and expand "audio_watermark"
4. Explore "Schemas" → "public" → "Tables" to see the `node`, `artist`, and `ArtistCollective` tables

### Troubleshooting PGAdmin 4 Connection

If you get "password authentication failed for user postgres":
- Verify the password is set correctly (see step 1 above)
- Use IP address `127.0.0.1` instead of `localhost` in the connection settings
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify TCP/IP connections are allowed in `pg_hba.conf` (should have `scram-sha-256` or `md5` authentication for 127.0.0.1)

## Running the Application

After database setup, start the Flask application:

```bash
python app.py
```

The application will be available at:
- Main page: http://127.0.0.1:5000/
- Artists page: http://127.0.0.1:5000/artists
- API endpoint: http://127.0.0.1:5000/api/nodes

## Troubleshooting

### Connection Issues

If you get "connection refused" errors:

1. Check if PostgreSQL is running:
```bash
# Linux/Mac
sudo systemctl status postgresql
# or
pg_ctl status

# Mac with Homebrew
brew services list
```

2. Start PostgreSQL if needed:
```bash
# Linux
sudo systemctl start postgresql

# Mac
brew services start postgresql
```

3. Verify port 5432 is open:
```bash
sudo lsof -i :5432
# or
netstat -an | grep 5432
```

### Authentication Issues

If you get authentication errors:

#### Setting the postgres user password

The application expects the postgres user to have the password `postgres`. Set this password:

```bash
# Connect as postgres user
sudo -u postgres psql

# Set the password
ALTER USER postgres WITH PASSWORD 'postgres';

# Exit
\q
```

#### For PGAdmin 4 Connection

When connecting via PGAdmin 4 or other GUI tools, use these settings:
- **Host**: 127.0.0.1 (or localhost)
- **Port**: 5432
- **Database**: audio_watermark
- **Username**: postgres
- **Password**: postgres

**Important**: Use the IP address `127.0.0.1` instead of `localhost` if you encounter connection issues. PGAdmin 4 may try to use Unix socket connections with `localhost`, which uses `peer` authentication by default.

#### Configuring pg_hba.conf (if needed)

If you still have issues, check PostgreSQL's `pg_hba.conf` file:

1. Find the file location (usually `/etc/postgresql/16/main/pg_hba.conf` on Ubuntu)
2. Ensure these lines exist for TCP/IP connections:
```
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256
```

3. Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### Permission Issues

If you get permission errors:

```bash
# Grant necessary permissions
sudo -u postgres psql -d audio_watermark
```

In PostgreSQL:
```sql
GRANT ALL PRIVILEGES ON DATABASE audio_watermark TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
```

## Database Schema

### Node Table

| Column | Type | Constraints | Indexed |
|--------|------|-------------|---------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Yes (PK) |
| name | CHAR(240) | NOT NULL | Yes |

### Sample Data

The database is populated with 19 globally diverse names from various countries:
- Nigeria, China, India, Saudi Arabia, Spain
- Japan, Egypt, Sweden, Russia, Ghana
- Brazil, Iran, Mexico, Senegal, Korea
- Ethiopia, Portugal, and more
