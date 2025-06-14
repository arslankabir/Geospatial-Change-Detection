import ee
import os

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

def download_landcover():
    """Download land cover data for Abu Dhabi."""
    # Initialize GEE
    if not initialize_gee():
        return
    
    # Define region of interest (Abu Dhabi)
    point = ee.Geometry.Point([54.37, 24.45])  # Abu Dhabi coordinates
    region = point.buffer(10000)  # 10km buffer
    
    # Get ESA WorldCover 2021
    landcover = ee.ImageCollection('ESA/WorldCover/v100').first()
    
    # Clip to region
    landcover = landcover.clip(region)
    
    # Export to Google Drive
    task = ee.batch.Export.image.toDrive(
        image=landcover,
        description='abudhabi_landcover',
        scale=10,
        region=region,
        fileFormat='GeoTIFF',
        folder='EarthEngine'
    )
    
    # Start the export task
    task.start()
    print("Export task started. Check your Google Drive for the file 'abudhabi_landcover.tif'")
    print("The file will be available in your Google Drive under the 'EarthEngine' folder.")
    print("Please download it to your project's 'data' directory.")

if __name__ == "__main__":
    download_landcover() 