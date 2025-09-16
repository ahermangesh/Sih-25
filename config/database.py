"""
Database configuration settings for PostgreSQL connection.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_CONFIG: Dict[str, Any] = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'ocean_db'),
    'username': os.getenv('DB_USER', 'sammy'),
    'password': os.getenv('DB_PASSWORD', ''),  # Set this via environment variable
}

def get_database_url() -> str:
    """
    Construct PostgreSQL database URL for SQLAlchemy.
    
    Returns:
        str: Database URL in the format postgresql://user:password@host:port/database
    """
    config = DATABASE_CONFIG
    return f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

def get_connection_params() -> Dict[str, Any]:
    """
    Get database connection parameters for direct psycopg2 connection.
    
    Returns:
        Dict[str, Any]: Dictionary containing connection parameters
    """
    return {
        'host': DATABASE_CONFIG['host'],
        'port': DATABASE_CONFIG['port'],
        'database': DATABASE_CONFIG['database'],
        'user': DATABASE_CONFIG['username'],
        'password': DATABASE_CONFIG['password']
    }
