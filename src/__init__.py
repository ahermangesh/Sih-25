"""
SIH'25 Ocean Data Analysis Package

This package provides tools for querying and analyzing ocean data from ARGO datasets.
"""

from .ocean_data_query import (
    OceanDataQuery,
    get_sample_data,
    get_data_count,
    query_by_location,
    query_by_date_range,
    get_data_summary,
    OceanDataQueryError
)

__version__ = "1.0.0"
__author__ = "SIH'25 Team"

__all__ = [
    'OceanDataQuery',
    'get_sample_data',
    'get_data_count',
    'query_by_location',
    'query_by_date_range',
    'get_data_summary',
    'OceanDataQueryError'
]
