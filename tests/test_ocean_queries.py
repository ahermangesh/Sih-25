"""
Comprehensive test script for Ocean Data Query Module

This script tests all the query functions with various scenarios
including edge cases and error handling.
"""

import sys
import os
import json
from datetime import date, datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from ocean_data_query import (
        OceanDataQuery, 
        get_sample_data, 
        get_data_count,
        query_by_location,
        query_by_date_range,
        get_data_summary,
        OceanDataQueryError
    )
except ImportError as e:
    print(f"Error importing ocean_data_query module: {e}")
    print("Make sure the database is set up and data is loaded.")
    sys.exit(1)


def print_test_result(test_name: str, result: dict, show_data: bool = False):
    """Helper function to print test results"""
    print(f"\n{'='*50}")
    print(f"TEST: {test_name}")
    print(f"{'='*50}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")
    
    if 'metadata' in result:
        print(f"Metadata: {json.dumps(result['metadata'], indent=2)}")
    
    if show_data and result['data']:
        print(f"Data preview: {json.dumps(result['data'][:2] if isinstance(result['data'], list) else result['data'], indent=2)}")
    
    print(f"Timestamp: {result['timestamp']}")


def test_sample_data():
    """Test get_sample_data function"""
    print("\n🧪 Testing get_sample_data function...")
    
    # Test 1: Normal case
    result = get_sample_data(5)
    print_test_result("Get Sample Data (5 records)", result, show_data=True)
    
    # Test 2: Edge case - single record
    result = get_sample_data(1)
    print_test_result("Get Sample Data (1 record)", result)
    
    # Test 3: Error case - invalid limit
    result = get_sample_data(0)
    print_test_result("Get Sample Data (invalid limit)", result)


def test_data_count():
    """Test get_data_count function"""
    print("\n🧪 Testing get_data_count function...")
    
    result = get_data_count()
    print_test_result("Get Total Data Count", result, show_data=True)


def test_location_queries():
    """Test query_by_location function"""
    print("\n🧪 Testing query_by_location function...")
    
    # Test 1: Indian Ocean region
    result = query_by_location(
        lat_range=(-10, 10),
        lon_range=(60, 80),
        limit=5
    )
    print_test_result("Query by Location (Indian Ocean)", result, show_data=True)
    
    # Test 2: Smaller region
    result = query_by_location(
        lat_range=(0, 5),
        lon_range=(63, 65),
        limit=3
    )
    print_test_result("Query by Location (Smaller region)", result)
    
    # Test 3: Error case - invalid latitude
    result = query_by_location(
        lat_range=(-100, 100),
        lon_range=(60, 80),
        limit=5
    )
    print_test_result("Query by Location (Invalid latitude)", result)
    
    # Test 4: Error case - invalid longitude
    result = query_by_location(
        lat_range=(-10, 10),
        lon_range=(-200, 200),
        limit=5
    )
    print_test_result("Query by Location (Invalid longitude)", result)


def test_date_queries():
    """Test query_by_date_range function"""
    print("\n🧪 Testing query_by_date_range function...")
    
    # Test 1: String dates
    result = query_by_date_range(
        start_date="2019-01-29",
        end_date="2019-01-30",
        limit=5
    )
    print_test_result("Query by Date Range (String dates)", result, show_data=True)
    
    # Test 2: Date objects
    result = query_by_date_range(
        start_date=date(2019, 1, 29),
        end_date=date(2019, 1, 29),
        limit=3
    )
    print_test_result("Query by Date Range (Date objects)", result)
    
    # Test 3: Error case - invalid date format
    result = query_by_date_range(
        start_date="2019/01/29",
        end_date="2019-01-30",
        limit=5
    )
    print_test_result("Query by Date Range (Invalid format)", result)
    
    # Test 4: Error case - start date after end date
    result = query_by_date_range(
        start_date="2019-01-30",
        end_date="2019-01-29",
        limit=5
    )
    print_test_result("Query by Date Range (Invalid range)", result)


def test_data_summary():
    """Test get_data_summary function"""
    print("\n🧪 Testing get_data_summary function...")
    
    result = get_data_summary()
    print_test_result("Get Data Summary", result, show_data=True)


def test_class_usage():
    """Test using the OceanDataQuery class directly"""
    print("\n🧪 Testing OceanDataQuery class usage...")
    
    try:
        # Initialize the class
        query_handler = OceanDataQuery()
        
        # Test method call
        result = query_handler.get_sample_data(3)
        print_test_result("Class Method Call", result)
        
        print("✅ Class instantiation and method call successful")
        
    except Exception as e:
        print(f"❌ Class test failed: {e}")


def test_performance():
    """Test performance with larger queries"""
    print("\n🧪 Testing performance with larger queries...")
    
    import time
    
    # Time a larger sample query
    start_time = time.time()
    result = get_sample_data(100)
    end_time = time.time()
    
    print(f"Sample data query (100 records) took: {end_time - start_time:.2f} seconds")
    print_test_result("Performance Test (100 records)", result)
    
    # Time a location query
    start_time = time.time()
    result = query_by_location(
        lat_range=(-20, 20),
        lon_range=(50, 90),
        limit=1000
    )
    end_time = time.time()
    
    print(f"Location query (up to 1000 records) took: {end_time - start_time:.2f} seconds")
    print_test_result("Performance Test (Location query)", result)


def main():
    """Run all tests"""
    print("🚀 Starting Ocean Data Query Module Tests")
    print("=" * 60)
    
    try:
        # Run all test functions
        test_sample_data()
        test_data_count()
        test_location_queries()
        test_date_queries()
        test_data_summary()
        test_class_usage()
        test_performance()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS COMPLETED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
