import ee
import os
from datetime import datetime, timedelta
import rasterio
from rasterio.transform import from_origin
import numpy as np

def initialize_gee():
    """Initialize Google Earth Engine."""
    try:
        ee.Initialize()
        print("Google Earth Engine initialized successfully.")
    except Exception as e:
        print(f"Error initializing Google Earth Engine: {e}")
        print("Please authenticate first using ee.Authenticate()")

def get_sentinel_image(roi, start_date, end_date, cloud_cover=10):
    """
    Get Sentinel-2 image for the specified region and date range.
    
    Args:
        roi (ee.Geometry): Region of interest
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        cloud_cover (int): Maximum cloud cover percentage
    
    Returns:
        ee.Image: Processed Sentinel-2 image
    """
    # Get Sentinel-2 collection
    sentinel = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filterBounds(roi) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_cover))
    
    # Get the least cloudy image
    image = sentinel.sort('CLOUDY_PIXEL_PERCENTAGE').first()
    
    # Select relevant bands
    bands = ['B2', 'B3', 'B4', 'B8', 'B11']  # Blue, Green, Red, NIR, SWIR
    image = image.select(bands)
    
    return image

def export_to_geotiff(image, roi, filename, scale=10):
    """
    Export Earth Engine image to GeoTIFF.
    
    Args:
        image (ee.Image): Earth Engine image to export
        roi (ee.Geometry): Region of interest
        filename (str): Output filename
        scale (int): Resolution in meters
    """
    task = ee.batch.Export.image.toDrive(
        image=image,
        description=filename,
        scale=scale,
        region=roi,
        fileFormat='GeoTIFF',
        maxPixels=1e13
    )
    task.start()
    print(f"Export task started for {filename}")
    return task

def main():
    # Initialize GEE
    initialize_gee()
    
    # Define Abu Dhabi region of interest
    abu_dhabi = ee.Geometry.Point([54.37, 24.45]).buffer(10000)  # 10km buffer around Abu Dhabi
    
    # Define time periods
    periods = {
        '2017': ('2017-01-01', '2017-03-31'),
        '2023': ('2023-01-01', '2023-03-31')
    }
    
    # Process each time period
    for year, (start_date, end_date) in periods.items():
        print(f"\nProcessing {year}...")
        
        # Get Sentinel-2 image
        image = get_sentinel_image(abu_dhabi, start_date, end_date)
        
        # Export to GeoTIFF
        filename = f"sentinel2_abudhabi_{year}"
        task = export_to_geotiff(image, abu_dhabi, filename)
        
        print(f"Image for {year} will be exported to your Google Drive.")

if __name__ == "__main__":
    main() 