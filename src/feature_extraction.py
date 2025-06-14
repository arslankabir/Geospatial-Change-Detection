import rasterio
import numpy as np
import os

def calculate_ndvi(nir, red):
    """
    Calculate Normalized Difference Vegetation Index (NDVI).
    
    Args:
        nir (numpy.ndarray): Near Infrared band
        red (numpy.ndarray): Red band
    
    Returns:
        numpy.ndarray: NDVI values
    """
    return (nir - red) / (nir + red + 1e-6)

def calculate_ndwi(green, nir):
    """
    Calculate Normalized Difference Water Index (NDWI).
    
    Args:
        green (numpy.ndarray): Green band
        nir (numpy.ndarray): Near Infrared band
    
    Returns:
        numpy.ndarray: NDWI values
    """
    return (green - nir) / (green + nir + 1e-6)

def calculate_ndbi(swir, nir):
    """
    Calculate Normalized Difference Built-up Index (NDBI).
    
    Args:
        swir (numpy.ndarray): Short Wave Infrared band
        nir (numpy.ndarray): Near Infrared band
    
    Returns:
        numpy.ndarray: NDBI values
    """
    return (swir - nir) / (swir + nir + 1e-6)

def calculate_savi(nir, red, L=0.5):
    """Calculate Soil Adjusted Vegetation Index."""
    return ((nir - red) * (1 + L)) / (nir + red + L + 1e-6)

def calculate_msavi(nir, red):
    """Calculate Modified Soil Adjusted Vegetation Index."""
    return (2 * nir + 1 - np.sqrt((2 * nir + 1)**2 - 8 * (nir - red))) / 2

def calculate_evi(nir, red, blue):
    """Calculate Enhanced Vegetation Index."""
    return 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1 + 1e-6)

def calculate_bsi(swir, nir, red, blue):
    """Calculate Bare Soil Index."""
    return ((swir + red) - (nir + blue)) / ((swir + red) + (nir + blue) + 1e-6)

def extract_features(sentinel_data):
    """Extract all spectral indices from Sentinel-2 data."""
    # Extract bands
    blue = sentinel_data[0]  # B2
    green = sentinel_data[1]  # B3
    red = sentinel_data[2]   # B4
    nir = sentinel_data[3]   # B8
    swir1 = sentinel_data[4] # B11
    swir2 = sentinel_data[5] # B12
    
    # Calculate indices
    features = {
        'NDVI': calculate_ndvi(nir, red),
        'NDWI': calculate_ndwi(green, nir),
        'NDBI': calculate_ndbi(swir1, nir),
        'SAVI': calculate_savi(nir, red),
        'MSAVI': calculate_msavi(nir, red),
        'EVI': calculate_evi(nir, red, blue),
        'BSI': calculate_bsi(swir1, nir, red, blue)
    }
    
    # Stack all features
    feature_stack = np.stack(list(features.values()))
    
    return feature_stack, list(features.keys())

def save_features(feature_stack, feature_names, output_path, meta):
    """Save extracted features to a GeoTIFF file."""
    # Update metadata
    meta.update({
        'count': len(feature_names),
        'dtype': 'float32'
    })
    
    # Save to file
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(feature_stack.astype('float32'))
        dst.descriptions = feature_names
    
    print(f"Features saved to {output_path}")
    print("Feature bands:", feature_names)

def main():
    # Example usage
    data_dir = "../data"
    sentinel_file = os.path.join(data_dir, "sentinel2_abudhabi_2023_preprocessed.tif")
    output_file = os.path.join(data_dir, "sentinel2_abudhabi_2023_features.tif")
    
    if os.path.exists(sentinel_file):
        with rasterio.open(sentinel_file) as src:
            sentinel_data = src.read()
            meta = src.meta
        
        # Extract features
        feature_stack, feature_names = extract_features(sentinel_data)
        
        # Save features
        save_features(feature_stack, feature_names, output_file, meta)
    else:
        print(f"Input file {sentinel_file} not found.")

if __name__ == "__main__":
    main() 