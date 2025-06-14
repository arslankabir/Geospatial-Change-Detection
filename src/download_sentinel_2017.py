import ee
import os
from datetime import datetime, timedelta
import geemap

def initialize_gee():
    """Initialize Google Earth Engine with proper project setup."""
    try:
        # First authenticate
        ee.Authenticate()
        
        # Initialize with your project ID
        ee.Initialize(project='unique-acronym-445710-k6')
        
        print("Google Earth Engine initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing Google Earth Engine: {e}")
        return False

def download_sentinel_2018():
    """Download Sentinel-2 imagery for Abu Dhabi in 2018."""
    # Initialize GEE
    if not initialize_gee():
        return
    
    # Create output directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Define region of interest (Abu Dhabi, 10km buffer)
    point = ee.Geometry.Point([54.37, 24.45])  # Abu Dhabi coordinates
    region = point.buffer(10000)  # 10km buffer
    
    # Define time period (all of 2018)
    start_date = '2018-01-01'
    end_date = '2018-12-31'
    
    print("Searching for Sentinel-2 images...")
    # Get Sentinel-2 collection with higher cloud cover threshold
    collection = ee.ImageCollection('COPERNICUS/S2_SR') \
        .filterBounds(region) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40))
    
    # Count images in the collection
    count = collection.size().getInfo()
    print(f"Number of images found: {count}")
    if count == 0:
        print("No suitable Sentinel-2 image found for the specified region and date range. Try increasing the date range or cloud cover threshold.")
        return
    
    # Get the least cloudy image
    sentinel = collection.sort('CLOUDY_PIXEL_PERCENTAGE').first()
    print("Image found. Selecting bands...")
    # Select bands (B2, B3, B4, B8)
    sentinel = sentinel.select(['B2', 'B3', 'B4', 'B8'])
    
    # Define output file path
    output_file = 'data/sentinel2_abudhabi_2018.tif'
    
    print(f"Downloading image to {output_file}...")
    try:
        # Download directly to local machine
        geemap.ee_export_image(
            sentinel,
            filename=output_file,
            scale=20,  # Reduced scale to 20m
            region=region,
            crs='EPSG:4326'
        )
        print(f"\nDownload complete! File saved to: {output_file}")
    except Exception as e:
        print(f"Error during download: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Make sure you have enough disk space")
        print("3. Verify that the Earth Engine API is enabled")
        print("4. Try running the script again")

if __name__ == "__main__":
    download_sentinel_2018() 