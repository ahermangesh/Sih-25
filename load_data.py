"""
PostgreSQL Ocean Database Connection and Data Loading Script

This script handles:
1. Database connection testing
2. ARGO data loading from CSV
3. Basic data validation

For query examples, run: python src/ocean_data_query.py
For comprehensive tests, run: python tests/test_ocean_queries.py
"""

import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os
import sys
from typing import Optional, Dict, Any

# Add the config directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))

try:
    from database import get_database_url, get_connection_params, DATABASE_CONFIG
except ImportError:
    print("Error: Could not import database configuration. Make sure config/database.py exists.")
    sys.exit(1)


def test_postgresql_connection() -> bool:
    """
    Test the PostgreSQL database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    print("Testing PostgreSQL connection...")
    print(f"Host: {DATABASE_CONFIG['host']}")
    print(f"Port: {DATABASE_CONFIG['port']}")
    print(f"Database: {DATABASE_CONFIG['database']}")
    print(f"User: {DATABASE_CONFIG['username']}")
    
    try:
        # Test with psycopg2 directly
        conn_params = get_connection_params()
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"✓ PostgreSQL connection successful!")
        print(f"Database version: {db_version[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def test_sqlalchemy_connection() -> bool:
    """
    Test the SQLAlchemy database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    print("\nTesting SQLAlchemy connection...")
    
    try:
        # Create SQLAlchemy engine
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database(), current_user;"))
            row = result.fetchone()
            print(f"✓ SQLAlchemy connection successful!")
            print(f"Connected to database: {row[0]} as user: {row[1]}")
            
        return True
        
    except SQLAlchemyError as e:
        print(f"✗ SQLAlchemy connection failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def check_table_exists(table_name: str) -> bool:
    """
    Check if a table exists in the database.
    
    Args:
        table_name (str): Name of the table to check
        
    Returns:
        bool: True if table exists, False otherwise
    """
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = :table_name
                );
            """), {"table_name": table_name})
            
            exists = result.fetchone()[0]
            print(f"Table '{table_name}' {'exists' if exists else 'does not exist'}")
            return exists
            
    except Exception as e:
        print(f"Error checking table existence: {e}")
        return False


def load_argo_data(csv_file_path: str, table_name: str = "argo_data") -> bool:
    """
    Load ARGO data from CSV file into PostgreSQL database.
    
    Args:
        csv_file_path (str): Path to the CSV file
        table_name (str): Name of the target table
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if CSV file exists
        if not os.path.exists(csv_file_path):
            print(f"Error: CSV file not found at {csv_file_path}")
            return False
        
        print(f"\nLoading data from {csv_file_path}...")
        
        # Read CSV file
        df = pd.read_csv(csv_file_path)
        print(f"Loaded {len(df)} rows from CSV")
        print(f"Columns: {list(df.columns)}")
        
        # Create database connection
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # Load data to database
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"✓ Data successfully loaded to table '{table_name}'")
        
        return True
        
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        return False


def main():
    """
    Main function to test connections and optionally load data.
    """
    print("=== PostgreSQL Ocean Database Setup Test ===\n")
    
    # Test connections
    pg_success = test_postgresql_connection()
    sqlalchemy_success = test_sqlalchemy_connection()
    
    if not (pg_success and sqlalchemy_success):
        print("\n⚠️  Connection tests failed. Please check your database configuration.")
        print("Make sure:")
        print("1. PostgreSQL is running")
        print("2. Database 'ocean_db' exists")
        print("3. User 'sammy' has proper permissions")
        print("4. Password is set correctly (use .env file)")
        return
    
    print("\n✓ All connection tests passed!")
    
    # Check if ARGO data file exists and offer to load it
    argo_file = "ARGO_2019.csv"
    if os.path.exists(argo_file):
        print(f"\nFound ARGO data file: {argo_file}")
        
        # Show file info
        df_preview = pd.read_csv(argo_file, nrows=5)
        print(f"File contains {len(pd.read_csv(argo_file))} rows")
        print("Preview of first 5 rows:")
        print(df_preview)
        
        response = input("\nWould you like to load this data into the database? (y/n): ")
        if response.lower() == 'y':
            load_argo_data(argo_file)
    else:
        print(f"\nARGO data file '{argo_file}' not found in current directory.")


if __name__ == "__main__":
    main()