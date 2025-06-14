import ee
import os
from datetime import datetime, timedelta

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

def estimate_image_size(region, scale):
    """Estimate the size of the image in pixels and MB."""
    # Get region bounds
    bounds = region.bounds().getInfo()
    coords = bounds['coordinates'][0]
    
    # Calculate width and height in degrees
    width_deg = abs(coords[1][0] - coords[0][0])
    height_deg = abs(coords[2][1] - coords[0][1])
    
    # Convert to meters (approximate)
    width_m = width_deg * 111320 * abs(coords[0][1])  # 111320 meters per degree at equator
    height_m = height_deg * 111320
    
    # Calculate pixels
    width_pixels = int(width_m / scale)
    height_pixels = int(height_m / scale)
    
    # Estimate size in MB (4 bands, 32-bit float)
    size_mb = (width_pixels * height_pixels * 4 * 4) / (1024 * 1024)
    
    return width_pixels, height_pixels, size_mb

def download_sentinel_2018():
    """Download Sentinel-2 imagery for Abu Dhabi in 2018 with matching parameters to 2023 image."""
    # Initialize GEE
    if not initialize_gee():
        return
    
    # Create output directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Define region of interest (Abu Dhabi, 20km buffer)
    point = ee.Geometry.Point([54.37, 24.45])  # Abu Dhabi coordinates
    region = point.buffer(20000)  # 20km buffer
    
    # Define scale
    scale = 30  # 30m scale to match 2023 image
    
    # Estimate image size
    width_pixels, height_pixels, size_mb = estimate_image_size(region, scale)
    print(f"\nEstimated image size:")
    print(f"  Width: {width_pixels} pixels")
    print(f"  Height: {height_pixels} pixels")
    print(f"  Total pixels: {width_pixels * height_pixels:,}")
    print(f"  Estimated size: {size_mb:.2f} MB")
    
    # Define time period (all of 2018)
    start_date = '2018-01-01'
    end_date = '2018-12-31'
    
    print("\nSearching for Sentinel-2 images...")
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
    
    # Export to Google Drive
    print("\nStarting export to Google Drive...")
    task = ee.batch.Export.image.toDrive(
        image=sentinel,
        description='sentinel2_abudhabi_2018',
        scale=scale,
        region=region,
        fileFormat='GeoTIFF',
        folder='EarthEngine',
        crs='EPSG:4326'  # Match CRS to 2023
    )
    
    # Start the export task
    task.start()
    print("\nExport task started!")
    print("The file will be exported to your Google Drive under the 'EarthEngine' folder.")
    print("Please follow these steps:")
    print("1. Wait a few minutes for the export to complete")
    print("2. Go to your Google Drive")
    print("3. Look for the 'EarthEngine' folder")
    print("4. Download the file 'sentinel2_abudhabi_2018.tif'")
    print("5. Move the file to your project's 'data' directory")
    print("\nYou can check the status of your export tasks at:")
    print("https://code.earthengine.google.com/tasks")

if __name__ == "__main__":
    download_sentinel_2018() 