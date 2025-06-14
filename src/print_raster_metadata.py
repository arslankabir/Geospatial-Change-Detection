import rasterio
import os

def print_metadata(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    with rasterio.open(file_path) as src:
        print(f"\nMetadata for {file_path}:")
        print(f"  CRS: {src.crs}")
        print(f"  Width: {src.width}")
        print(f"  Height: {src.height}")
        print(f"  Count (bands): {src.count}")
        print(f"  Transform: {src.transform}")
        print(f"  Bounds: {src.bounds}")

def main():
    file_2018 = 'data/sentinel2_abudhabi_2018.tif'
    file_2023 = 'data/sentinel2_abudhabi_2023.tif'
    print_metadata(file_2018)
    print_metadata(file_2023)

if __name__ == "__main__":
    main() 