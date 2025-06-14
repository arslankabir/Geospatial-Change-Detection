import rasterio
import numpy as np
from rasterio.warp import calculate_default_transform, reproject, Resampling
import os

def read_sentinel_image(file_path):
    """
    Read Sentinel-2 image from GeoTIFF file.
    
    Args:
        file_path (str): Path to the GeoTIFF file
    
    Returns:
        tuple: (image_data, metadata)
    """
    with rasterio.open(file_path) as src:
        image = src.read()
        meta = src.meta
    return image, meta

def normalize_image(image):
    """
    Normalize image values to 0-1 range.
    
    Args:
        image (numpy.ndarray): Input image array
    
    Returns:
        numpy.ndarray: Normalized image
    """
    return (image - image.min()) / (image.max() - image.min())

def resample_image(image, meta, target_resolution=10):
    """
    Resample image to target resolution.
    
    Args:
        image (numpy.ndarray): Input image array
        meta (dict): Image metadata
        target_resolution (int): Target resolution in meters
    
    Returns:
        tuple: (resampled_image, updated_metadata)
    """
    # Calculate new transform and dimensions
    transform, width, height = calculate_default_transform(
        meta['crs'],
        meta['crs'],
        meta['width'],
        meta['height'],
        *meta['transform'],
        resolution=(target_resolution, target_resolution)
    )
    
    # Update metadata
    meta.update({
        'transform': transform,
        'width': width,
        'height': height
    })
    
    # Create output array
    resampled = np.zeros((meta['count'], height, width))
    
    # Reproject each band
    for i in range(meta['count']):
        reproject(
            source=image[i],
            destination=resampled[i],
            src_transform=meta['transform'],
            src_crs=meta['crs'],
            dst_transform=transform,
            dst_crs=meta['crs'],
            resampling=Resampling.bilinear
        )
    
    return resampled, meta

def save_preprocessed_image(image, meta, output_path):
    """
    Save preprocessed image to GeoTIFF.
    
    Args:
        image (numpy.ndarray): Image array
        meta (dict): Image metadata
        output_path (str): Output file path
    """
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(image)

def preprocess_sentinel_image(input_path, output_path, target_resolution=10):
    """
    Complete preprocessing pipeline for Sentinel-2 image.
    
    Args:
        input_path (str): Path to input GeoTIFF
        output_path (str): Path to save preprocessed image
        target_resolution (int): Target resolution in meters
    """
    # Read image
    image, meta = read_sentinel_image(input_path)
    
    # Normalize image
    normalized = normalize_image(image)
    
    # Resample image
    resampled, updated_meta = resample_image(normalized, meta, target_resolution)
    
    # Save preprocessed image
    save_preprocessed_image(resampled, updated_meta, output_path)
    
    print(f"Preprocessed image saved to {output_path}")

def main():
    # Example usage
    data_dir = "../data"
    input_file = os.path.join(data_dir, "sentinel2_abudhabi_2023.tif")
    output_file = os.path.join(data_dir, "sentinel2_abudhabi_2023_preprocessed.tif")
    
    if os.path.exists(input_file):
        preprocess_sentinel_image(input_file, output_file)
    else:
        print(f"Input file {input_file} not found.")

if __name__ == "__main__":
    main() 