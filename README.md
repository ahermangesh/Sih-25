# SIH'25 Ocean Database Project

This project is designed to work with PostgreSQL ocean database for loading and analyzing ARGO oceanographic data.

## Project Structure

```
Sih-25/
├── config/
│   ├── __init__.py          # Configuration package
│   └── database.py          # Database connection settings
├── src/
│   ├── __init__.py          # Source package
│   └── ocean_data_query.py  # Main query module  
├── tests/
│   ├── __init__.py          # Tests package
│   └── test_ocean_queries.py # Comprehensive test suite
├── ARGO_2019.csv           # ARGO oceanographic data
├── load_data.py            # Main data loading script
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Prerequisites

1. **PostgreSQL** installed and running
2. **Python 3.8+** installed
3. A PostgreSQL database named `ocean_db`
4. A PostgreSQL user named `sammy` with appropriate permissions

## Setup Instructions

### 1. Database Setup

Make sure you have PostgreSQL running with:
- Database: `ocean_db`
- User: `sammy`
- Appropriate permissions for the user

### 2. Python Environment Setup

Install the required packages:

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pandas sqlalchemy psycopg2-binary python-dotenv
```

### 3. Environment Configuration

1. Copy the environment template:
   ```bash
   copy .env.example .env
   ```

2. Edit the `.env` file with your database credentials:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=ocean_db
   DB_USER=sammy
   DB_PASSWORD=your_actual_password
   ```

### 4. Test the Connection

Run the data loading script which includes connection testing:
```bash
python load_data.py
```

### Testing

Run the comprehensive test suite:
```bash
python tests/test_ocean_queries.py
```

## Features

- ✅ PostgreSQL connection testing
- ✅ SQLAlchemy integration
- ✅ Environment-based configuration
- ✅ ARGO data loading from CSV
- ✅ Error handling and user feedback
- ✅ Table existence checking

## Troubleshooting

### Connection Issues

1. **Database not found**: Make sure `ocean_db` database exists
2. **User permissions**: Ensure user `sammy` has proper permissions
3. **Password**: Check your `.env` file has the correct password
4. **PostgreSQL not running**: Start your PostgreSQL service

### Common Commands

Create database (if needed):
```sql
CREATE DATABASE ocean_db;
CREATE USER sammy WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ocean_db TO sammy;
```

## Dependencies

- `pandas`: Data manipulation and analysis
- `sqlalchemy`: SQL toolkit and ORM
- `psycopg2-binary`: PostgreSQL adapter for Python
- `python-dotenv`: Environment variable management

## Phase 2 - Data Access Functions

### Ocean Data Query Module

The `src/ocean_data_query.py` module provides reusable Python functions to query ocean data efficiently with:

- ✅ **Geographic filtering** (by lat/lon coordinates)
- ✅ **Temporal filtering** (by date ranges)  
- ✅ **Sample data retrieval**
- ✅ **Record counting and aggregation**
- ✅ **Consistent JSON-ready response formats**
- ✅ **Parameter validation and sanitization**
- ✅ **Error handling for database issues**
- ✅ **Performance optimization for large datasets**

### Available Query Functions

#### 1. `get_sample_data(limit=5)`
Get sample records from the ocean data.

```python
from src.ocean_data_query import get_sample_data

# Get 10 sample records
result = get_sample_data(10)
if result['success']:
    records = result['data']
    print(f"Retrieved {len(records)} records")
```

#### 2. `get_data_count()`
Get total record count from the database.

```python
from src.ocean_data_query import get_data_count

result = get_data_count()
if result['success']:
    total = result['data']['total_records']
    print(f"Total records: {total:,}")
```

#### 3. `query_by_location(lat_range, lon_range, limit=100)`
Filter data by geographic coordinates.

```python
from src.ocean_data_query import query_by_location

# Query Indian Ocean region
result = query_by_location(
    lat_range=(-10, 10),    # 10°S to 10°N
    lon_range=(60, 80),     # 60°E to 80°E
    limit=50
)
```

#### 4. `query_by_date_range(start_date, end_date, limit=100)`
Filter data by date range.

```python
from src.ocean_data_query import query_by_date_range

# Query specific date range
result = query_by_date_range(
    start_date="2019-01-29",
    end_date="2019-01-30",
    limit=100
)
```

#### 5. `get_data_summary()`
Get comprehensive dataset statistics.

```python
from src.ocean_data_query import get_data_summary

result = get_data_summary()
if result['success']:
    summary = result['data']
    print(f"Total records: {summary['dataset_overview']['total_records']}")
    print(f"Geographic extent: {summary['geographic_extent']}")
```

### Response Format

All functions return consistent JSON-ready responses:

```python
{
    "success": true,
    "timestamp": "2025-09-16T...",
    "message": "Retrieved 5 sample records",
    "data": [...],  # Actual data
    "metadata": {   # Query information
        "query_type": "sample_data",
        "limit": 5,
        "returned_records": 5,
        "columns": ["datetime", "time", "lon", "lat", "mld"]
    }
}
```

### Class-Based Usage

For advanced usage, you can use the `OceanDataQuery` class directly:

```python
from src.ocean_data_query import OceanDataQuery

# Initialize query handler
query_handler = OceanDataQuery(table_name="argo_data")

# Use methods
result = query_handler.get_sample_data(10)
location_result = query_handler.query_by_location((-5, 5), (60, 70))
```

### Testing

Run the comprehensive test suite:

```bash
python tests/test_ocean_queries.py
```

Run usage examples:

```bash
python src/ocean_data_query.py
```

### Error Handling

All functions include comprehensive error handling:

- **Parameter validation**: Validates coordinates, dates, and limits
- **Database errors**: Graceful handling of connection issues
- **Data sanitization**: Converts NaN values to None for JSON compatibility
- **Custom exceptions**: `OceanDataQueryError` for specific issues

### Performance Optimization

- **Parameterized queries**: Prevents SQL injection
- **Limit enforcement**: Maximum 10,000 records per query
- **Efficient indexing**: Optimized for datetime and coordinate queries
- **Memory management**: Streaming results for large datasets

This data access layer is now ready for AI chatbot integration, providing efficient and reliable access to ocean data with proper error handling and validation.
