import ee

def initialize_gee():
    """Initialize Google Earth Engine with proper project setup."""
    try:
        # First authenticate
        ee.Authenticate()
        
        # Initialize with your project ID
        # Replace 'your-project-id' with your actual Google Cloud Project ID
        ee.Initialize(project='unique-acronym-445710-k6')
        
        print("Google Earth Engine initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing Google Earth Engine: {e}")
        return False

if __name__ == "__main__":
    initialize_gee() 