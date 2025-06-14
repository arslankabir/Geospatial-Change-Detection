import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os

def calculate_ndvi(image):
    nir = image[3].astype(float)
    red = image[2].astype(float)
    denominator = (nir + red)
    denominator[denominator == 0] = np.nan
    return (nir - red) / denominator

def calculate_ndwi(image):
    green = image[1].astype(float)
    nir = image[3].astype(float)
    denominator = (green + nir)
    denominator[denominator == 0] = np.nan
    return (green - nir) / denominator

def calculate_ndbi(image):
    swir = image[0].astype(float)  # B2 as SWIR placeholder (adjust if you have SWIR band)
    nir = image[3].astype(float)
    denominator = (swir + nir)
    denominator[denominator == 0] = np.nan
    return (swir - nir) / denominator

def load_sentinel_image(path):
    with rasterio.open(path) as src:
        image = src.read()
        meta = src.meta
        pixel_size_x = abs(src.transform[0])
        pixel_size_y = abs(src.transform[4])
    return image, meta, pixel_size_x, pixel_size_y

def detect_changes(image_2018, image_2023):
    ndvi_2018 = calculate_ndvi(image_2018)
    ndvi_2023 = calculate_ndvi(image_2023)
    ndvi_change = ndvi_2023 - ndvi_2018

    ndwi_2018 = calculate_ndwi(image_2018)
    ndwi_2023 = calculate_ndwi(image_2023)
    ndwi_change = ndwi_2023 - ndwi_2018

    ndbi_2018 = calculate_ndbi(image_2018)
    ndbi_2023 = calculate_ndbi(image_2023)
    ndbi_change = ndbi_2023 - ndbi_2018

    return {
        'ndvi': (ndvi_2018, ndvi_2023, ndvi_change),
        'ndwi': (ndwi_2018, ndwi_2023, ndwi_change),
        'ndbi': (ndbi_2018, ndbi_2023, ndbi_change)
    }

def plot_changes(index_name, index_2018, index_2023, change, out_dir):
    plt.figure(figsize=(18, 6))
    vmin = np.nanpercentile(change, 2)
    vmax = np.nanpercentile(change, 98)
    cmap = 'RdYlGn' if index_name == 'ndvi' else ('Blues' if index_name == 'ndwi' else 'bwr')

    plt.subplot(1, 3, 1)
    plt.title(f'{index_name.upper()} 2018')
    plt.imshow(index_2018, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar(label=index_name.upper())
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.title(f'{index_name.upper()} 2023')
    plt.imshow(index_2023, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar(label=index_name.upper())
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.title(f'{index_name.upper()} Change (2023-2018)')
    im = plt.imshow(change, cmap='bwr', vmin=-np.nanmax(np.abs(change)), vmax=np.nanmax(np.abs(change)))
    plt.colorbar(im, label='Change')
    plt.axis('off')

    plt.suptitle(f'{index_name.upper()} Change Detection', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_path = os.path.join(out_dir, f'{index_name}_changes.png')
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f'Saved: {out_path}')

def calculate_area_stats(change, pixel_size_x, pixel_size_y, threshold=0.1):
    # Only consider significant changes (above threshold)
    pos_mask = change > threshold
    neg_mask = change < -threshold
    pixel_area_km2 = (pixel_size_x * pixel_size_y) / 1e6
    pos_area = np.nansum(pos_mask) * pixel_area_km2
    neg_area = np.nansum(neg_mask) * pixel_area_km2
    return pos_area, neg_area

def main():
    file_2018 = 'data/sentinel2_abudhabi_2018.tif'
    file_2023 = 'data/sentinel2_abudhabi_2023.tif'
    out_dir = 'data'

    if not os.path.exists(file_2018) or not os.path.exists(file_2023):
        print('Sentinel-2 files not found.')
        return

    print('Loading Sentinel-2 images...')
    image_2018, meta, pixel_size_x, pixel_size_y = load_sentinel_image(file_2018)
    image_2023, _, _, _ = load_sentinel_image(file_2023)

    print('Performing change detection...')
    changes = detect_changes(image_2018, image_2023)

    print('Plotting results...')
    for index_name, (idx_2018, idx_2023, change) in changes.items():
        plot_changes(index_name, idx_2018, idx_2023, change, out_dir)
        pos_area, neg_area = calculate_area_stats(change, pixel_size_x, pixel_size_y)
        print(f'Area statistics for {index_name.upper()} changes:')
        print(f'  Positive change (>+0.1): {pos_area:.2f} km^2')
        print(f'  Negative change (<-0.1): {neg_area:.2f} km^2')
        print()
    print("Change detection complete! Results saved in the 'data' directory:")
    print('- ndvi_changes.png: Vegetation changes')
    print('- ndwi_changes.png: Water body changes')
    print('- ndbi_changes.png: Built-up area changes')

if __name__ == '__main__':
    main() 