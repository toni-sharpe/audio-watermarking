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

### 2. Create Database

After installing PostgreSQL, create the database:

```bash
# Switch to postgres user (Linux/Mac)
sudo -u postgres psql

# Or connect directly (if already configured)
psql -U postgres
```

In the PostgreSQL prompt:
```sql
CREATE DATABASE audio_watermark;
\q
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
  - `name`: VARCHAR(240) field (indexed)
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

1. Edit PostgreSQL's `pg_hba.conf` file (location varies by OS)
2. Add/modify line for local connections:
```
local   all   postgres   trust
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
| name | VARCHAR(240) | NOT NULL | Yes |

### Sample Data

The database is populated with 19 globally diverse names from various countries:
- Nigeria, China, India, Saudi Arabia, Spain
- Japan, Egypt, Sweden, Russia, Ghana
- Brazil, Iran, Mexico, Senegal, Korea
- Ethiopia, Portugal, and more
