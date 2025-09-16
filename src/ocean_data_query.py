"""
Ocean Data Query Module for ARGO Oceanographic Data

This module provides reusable functions to query ocean data efficiently.
Includes geographic filtering, temporal filtering, and data aggregation functions.
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
from typing import Dict, List, Optional, Union, Tuple, Any
import json
import sys
import os

# Add config to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config'))

try:
    from database import get_database_url
except ImportError:
    print("Warning: Could not import database configuration")
    

class OceanDataQueryError(Exception):
    """Custom exception for ocean data query errors"""
    pass


class OceanDataQuery:
    """
    Class to handle all ocean data queries with proper error handling,
    validation, and JSON-ready response formats.
    """
    
    def __init__(self, table_name: str = "argo_data"):
        """
        Initialize the query class.
        
        Args:
            table_name (str): Name of the database table containing ocean data
        """
        self.table_name = table_name
        self.engine = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            database_url = get_database_url()
            self.engine = create_engine(database_url)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
        except Exception as e:
            raise OceanDataQueryError(f"Failed to connect to database: {e}")
    
    def _validate_coordinates(self, lat_range: Tuple[float, float] = None, 
                            lon_range: Tuple[float, float] = None) -> bool:
        """
        Validate latitude and longitude ranges.
        
        Args:
            lat_range: Tuple of (min_lat, max_lat)
            lon_range: Tuple of (min_lon, max_lon)
            
        Returns:
            bool: True if valid
            
        Raises:
            OceanDataQueryError: If coordinates are invalid
        """
        if lat_range:
            min_lat, max_lat = lat_range
            if not (-90 <= min_lat <= max_lat <= 90):
                raise OceanDataQueryError(f"Invalid latitude range: {lat_range}. Must be between -90 and 90")
        
        if lon_range:
            min_lon, max_lon = lon_range
            if not (-180 <= min_lon <= max_lon <= 180):
                raise OceanDataQueryError(f"Invalid longitude range: {lon_range}. Must be between -180 and 180")
        
        return True
    
    def _validate_dates(self, start_date: Union[str, date], 
                       end_date: Union[str, date]) -> Tuple[str, str]:
        """
        Validate and convert dates to string format.
        
        Args:
            start_date: Start date (string or date object)
            end_date: End date (string or date object)
            
        Returns:
            Tuple[str, str]: Validated start and end dates as strings
            
        Raises:
            OceanDataQueryError: If dates are invalid
        """
        try:
            if isinstance(start_date, str):
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                start_str = start_date
            else:
                start_dt = datetime.combine(start_date, datetime.min.time())
                start_str = start_date.strftime("%Y-%m-%d")
            
            if isinstance(end_date, str):
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                end_str = end_date
            else:
                end_dt = datetime.combine(end_date, datetime.min.time())
                end_str = end_date.strftime("%Y-%m-%d")
            
            if start_dt > end_dt:
                raise OceanDataQueryError(f"Start date {start_str} must be before end date {end_str}")
            
            return start_str, end_str
            
        except ValueError as e:
            raise OceanDataQueryError(f"Invalid date format: {e}")
    
    def _format_response(self, data: Any, success: bool = True, 
                        message: str = "", metadata: Dict = None) -> Dict:
        """
        Format response in consistent JSON-ready format.
        
        Args:
            data: The actual data to return
            success: Whether the operation was successful
            message: Optional message
            metadata: Optional metadata about the query
            
        Returns:
            Dict: Formatted response
        """
        response = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "data": data
        }
        
        if metadata:
            response["metadata"] = metadata
            
        return response
    
    def get_sample_data(self, limit: int = 5) -> Dict:
        """
        Get sample records from the ocean data.
        
        Args:
            limit (int): Number of sample records to return (default: 5)
            
        Returns:
            Dict: JSON-ready response with sample data
        """
        try:
            if limit <= 0 or limit > 1000:
                raise OceanDataQueryError("Limit must be between 1 and 1000")
            
            query = f"""
            SELECT * FROM {self.table_name}
            ORDER BY datetime
            LIMIT :limit
            """
            
            with self.engine.connect() as conn:
                df = pd.read_sql(query, conn, params={"limit": limit})
            
            # Convert DataFrame to list of dictionaries for JSON serialization
            records = df.to_dict('records')
            
            # Convert any NaN values to None for JSON compatibility
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
            
            metadata = {
                "query_type": "sample_data",
                "limit": limit,
                "returned_records": len(records),
                "columns": list(df.columns) if not df.empty else []
            }
            
            return self._format_response(
                data=records,
                message=f"Retrieved {len(records)} sample records",
                metadata=metadata
            )
            
        except Exception as e:
            return self._format_response(
                data=[],
                success=False,
                message=f"Error retrieving sample data: {str(e)}"
            )
    
    def get_data_count(self) -> Dict:
        """
        Get total record count from the ocean data table.
        
        Returns:
            Dict: JSON-ready response with record count
        """
        try:
            query = f"SELECT COUNT(*) as total_records FROM {self.table_name}"
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                count = result.fetchone()[0]
            
            metadata = {
                "query_type": "data_count",
                "table_name": self.table_name
            }
            
            return self._format_response(
                data={"total_records": count},
                message=f"Total records in {self.table_name}: {count:,}",
                metadata=metadata
            )
            
        except Exception as e:
            return self._format_response(
                data={"total_records": 0},
                success=False,
                message=f"Error counting records: {str(e)}"
            )
    
    def query_by_location(self, lat_range: Tuple[float, float], 
                         lon_range: Tuple[float, float], limit: int = 100) -> Dict:
        """
        Query ocean data by geographic location (latitude and longitude ranges).
        
        Args:
            lat_range: Tuple of (min_latitude, max_latitude)
            lon_range: Tuple of (min_longitude, max_longitude)
            limit: Maximum number of records to return
            
        Returns:
            Dict: JSON-ready response with filtered data
        """
        try:
            # Validate coordinates
            self._validate_coordinates(lat_range, lon_range)
            
            if limit <= 0 or limit > 10000:
                raise OceanDataQueryError("Limit must be between 1 and 10,000")
            
            min_lat, max_lat = lat_range
            min_lon, max_lon = lon_range
            
            query = f"""
            SELECT * FROM {self.table_name}
            WHERE lat BETWEEN :min_lat AND :max_lat
            AND lon BETWEEN :min_lon AND :max_lon
            ORDER BY datetime
            LIMIT :limit
            """
            
            params = {
                "min_lat": min_lat,
                "max_lat": max_lat,
                "min_lon": min_lon,
                "max_lon": max_lon,
                "limit": limit
            }
            
            with self.engine.connect() as conn:
                df = pd.read_sql(query, conn, params=params)
            
            # Convert to JSON-ready format
            records = df.to_dict('records')
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
            
            metadata = {
                "query_type": "location_filter",
                "filters": {
                    "latitude_range": lat_range,
                    "longitude_range": lon_range
                },
                "limit": limit,
                "returned_records": len(records),
                "columns": list(df.columns) if not df.empty else []
            }
            
            return self._format_response(
                data=records,
                message=f"Retrieved {len(records)} records for location query",
                metadata=metadata
            )
            
        except Exception as e:
            return self._format_response(
                data=[],
                success=False,
                message=f"Error querying by location: {str(e)}"
            )
    
    def query_by_date_range(self, start_date: Union[str, date], 
                           end_date: Union[str, date], limit: int = 100) -> Dict:
        """
        Query ocean data by date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD string or date object)
            end_date: End date (YYYY-MM-DD string or date object)
            limit: Maximum number of records to return
            
        Returns:
            Dict: JSON-ready response with filtered data
        """
        try:
            # Validate dates
            start_str, end_str = self._validate_dates(start_date, end_date)
            
            if limit <= 0 or limit > 10000:
                raise OceanDataQueryError("Limit must be between 1 and 10,000")
            
            query = f"""
            SELECT * FROM {self.table_name}
            WHERE datetime >= :start_date AND datetime <= :end_date
            ORDER BY datetime
            LIMIT :limit
            """
            
            params = {
                "start_date": start_str,
                "end_date": end_str,
                "limit": limit
            }
            
            with self.engine.connect() as conn:
                df = pd.read_sql(query, conn, params=params)
            
            # Convert to JSON-ready format
            records = df.to_dict('records')
            for record in records:
                for key, value in record.items():
                    if pd.isna(value):
                        record[key] = None
            
            metadata = {
                "query_type": "date_range_filter",
                "filters": {
                    "start_date": start_str,
                    "end_date": end_str
                },
                "limit": limit,
                "returned_records": len(records),
                "columns": list(df.columns) if not df.empty else []
            }
            
            return self._format_response(
                data=records,
                message=f"Retrieved {len(records)} records for date range {start_str} to {end_str}",
                metadata=metadata
            )
            
        except Exception as e:
            return self._format_response(
                data=[],
                success=False,
                message=f"Error querying by date range: {str(e)}"
            )
    
    def get_data_summary(self) -> Dict:
        """
        Get comprehensive dataset overview statistics.
        
        Returns:
            Dict: JSON-ready response with dataset statistics
        """
        try:
            # Get basic statistics
            summary_query = f"""
            SELECT 
                COUNT(*) as total_records,
                MIN(lat) as min_latitude,
                MAX(lat) as max_latitude,
                MIN(lon) as min_longitude,
                MAX(lon) as max_longitude,
                MIN(datetime) as earliest_date,
                MAX(datetime) as latest_date,
                AVG(mld) as avg_mixed_layer_depth,
                MIN(mld) as min_mixed_layer_depth,
                MAX(mld) as max_mixed_layer_depth,
                COUNT(DISTINCT datetime) as unique_dates
            FROM {self.table_name}
            WHERE mld IS NOT NULL
            """
            
            with self.engine.connect() as conn:
                summary_result = conn.execute(text(summary_query))
                summary_row = summary_result.fetchone()
                
                # Get record count per month/year for temporal distribution
                temporal_query = f"""
                SELECT 
                    EXTRACT(YEAR FROM datetime::date) as year,
                    EXTRACT(MONTH FROM datetime::date) as month,
                    COUNT(*) as record_count
                FROM {self.table_name}
                GROUP BY EXTRACT(YEAR FROM datetime::date), EXTRACT(MONTH FROM datetime::date)
                ORDER BY year, month
                LIMIT 12
                """
                temporal_df = pd.read_sql(temporal_query, conn)
            
            # Format summary data
            summary_data = {
                "dataset_overview": {
                    "total_records": int(summary_row[0]) if summary_row[0] else 0,
                    "unique_dates": int(summary_row[10]) if summary_row[10] else 0,
                    "date_range": {
                        "earliest": str(summary_row[5]) if summary_row[5] else None,
                        "latest": str(summary_row[6]) if summary_row[6] else None
                    }
                },
                "geographic_extent": {
                    "latitude_range": {
                        "min": float(summary_row[1]) if summary_row[1] else None,
                        "max": float(summary_row[2]) if summary_row[2] else None
                    },
                    "longitude_range": {
                        "min": float(summary_row[3]) if summary_row[3] else None,
                        "max": float(summary_row[4]) if summary_row[4] else None
                    }
                },
                "mixed_layer_depth_stats": {
                    "average": float(summary_row[7]) if summary_row[7] else None,
                    "minimum": float(summary_row[8]) if summary_row[8] else None,
                    "maximum": float(summary_row[9]) if summary_row[9] else None
                },
                "temporal_distribution": temporal_df.to_dict('records')
            }
            
            metadata = {
                "query_type": "data_summary",
                "generated_at": datetime.now().isoformat(),
                "table_name": self.table_name
            }
            
            return self._format_response(
                data=summary_data,
                message="Dataset summary generated successfully",
                metadata=metadata
            )
            
        except Exception as e:
            return self._format_response(
                data={},
                success=False,
                message=f"Error generating data summary: {str(e)}"
            )


# Convenience functions for direct use
def get_sample_data(limit: int = 5, table_name: str = "argo_data") -> Dict:
    """Convenience function to get sample data"""
    query_handler = OceanDataQuery(table_name)
    return query_handler.get_sample_data(limit)


def get_data_count(table_name: str = "argo_data") -> Dict:
    """Convenience function to get data count"""
    query_handler = OceanDataQuery(table_name)
    return query_handler.get_data_count()


def query_by_location(lat_range: Tuple[float, float], 
                     lon_range: Tuple[float, float], 
                     limit: int = 100, 
                     table_name: str = "argo_data") -> Dict:
    """Convenience function to query by location"""
    query_handler = OceanDataQuery(table_name)
    return query_handler.query_by_location(lat_range, lon_range, limit)


def query_by_date_range(start_date: Union[str, date], 
                       end_date: Union[str, date], 
                       limit: int = 100, 
                       table_name: str = "argo_data") -> Dict:
    """Convenience function to query by date range"""
    query_handler = OceanDataQuery(table_name)
    return query_handler.query_by_date_range(start_date, end_date, limit)


def get_data_summary(table_name: str = "argo_data") -> Dict:
    """Convenience function to get data summary"""
    query_handler = OceanDataQuery(table_name)
    return query_handler.get_data_summary()


if __name__ == "__main__":
    """
    Example usage and testing
    """
    print("=== Ocean Data Query Module Test ===\n")
    
    try:
        # Test basic functions
        print("1. Testing get_sample_data()...")
        sample_result = get_sample_data(3)
        print(f"   Success: {sample_result['success']}")
        print(f"   Message: {sample_result['message']}")
        
        print("\n2. Testing get_data_count()...")
        count_result = get_data_count()
        print(f"   Success: {count_result['success']}")
        print(f"   Message: {count_result['message']}")
        
        print("\n3. Testing get_data_summary()...")
        summary_result = get_data_summary()
        print(f"   Success: {summary_result['success']}")
        print(f"   Message: {summary_result['message']}")
        
        # Example location query (Indian Ocean region)
        print("\n4. Testing query_by_location()...")
        location_result = query_by_location(
            lat_range=(-10, 10),
            lon_range=(60, 80),
            limit=5
        )
        print(f"   Success: {location_result['success']}")
        print(f"   Message: {location_result['message']}")
        
        # Example date range query
        print("\n5. Testing query_by_date_range()...")
        date_result = query_by_date_range(
            start_date="2019-01-29",
            end_date="2019-01-30",
            limit=5
        )
        print(f"   Success: {date_result['success']}")
        print(f"   Message: {date_result['message']}")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
