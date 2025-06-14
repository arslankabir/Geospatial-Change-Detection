import numpy as np
import matplotlib.pyplot as plt
import rasterio
from rasterio.warp import Resampling
import os

def load_classification(year, data_dir):
    """Load classification results for a specific year."""
    file_path = os.path.join(data_dir, f"classification_result_{year}.tif")
    if not os.path.exists(file_path):
        print(f"Error: Classification file for {year} not found")
        return None
    
    with rasterio.open(file_path) as src:
        return src.read(1)

def calculate_changes(class_2017, class_2023):
    """Calculate land cover changes between 2017 and 2023."""
    # Initialize change matrix
    n_classes = 4
    change_matrix = np.zeros((n_classes, n_classes), dtype=int)
    
    # Calculate changes
    for i in range(1, n_classes + 1):
        for j in range(1, n_classes + 1):
            change_matrix[i-1, j-1] = np.sum((class_2017 == i) & (class_2023 == j))
    
    return change_matrix

def plot_change_matrix(change_matrix, output_path):
    """Plot the change matrix as a heatmap."""
    class_names = ['Water', 'Vegetation', 'Built-up', 'Barren']
    
    plt.figure(figsize=(10, 8))
    plt.imshow(change_matrix, cmap='YlOrRd')
    plt.colorbar(label='Number of Pixels')
    
    # Add labels
    plt.xticks(range(len(class_names)), class_names, rotation=45, ha='right')
    plt.yticks(range(len(class_names)), class_names)
    plt.xlabel('2023 Land Cover')
    plt.ylabel('2017 Land Cover')
    plt.title('Land Cover Change Matrix (2017-2023)')
    
    # Add text annotations
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            plt.text(j, i, f'{change_matrix[i, j]:,}',
                    ha='center', va='center',
                    color='black' if change_matrix[i, j] < np.max(change_matrix)/2 else 'white')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_change_map(class_2017, class_2023, output_path):
    """Plot a map showing areas of change."""
    # Create change map (0: no change, 1: change)
    change_map = (class_2017 != class_2023).astype(int)
    
    plt.figure(figsize=(12, 10))
    plt.imshow(change_map, cmap='binary')
    plt.colorbar(label='Change (1) / No Change (0)')
    plt.title('Land Cover Changes 2017-2023')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    data_dir = "data"
    
    # Load classifications
    class_2017 = load_classification(2017, data_dir)
    class_2023 = load_classification(2023, data_dir)
    
    if class_2017 is None or class_2023 is None:
        return
    
    # Calculate and plot change matrix
    change_matrix = calculate_changes(class_2017, class_2023)
    plot_change_matrix(change_matrix, os.path.join(data_dir, 'change_matrix.png'))
    
    # Plot change map
    plot_change_map(class_2017, class_2023, os.path.join(data_dir, 'change_map.png'))
    
    # Print summary statistics
    total_pixels = np.sum(change_matrix)
    print("\nChange Summary (2017-2023):")
    print(f"Total pixels analyzed: {total_pixels:,}")
    print(f"Pixels with changes: {np.sum(change_matrix) - np.sum(np.diag(change_matrix)):,}")
    print(f"Percentage of area changed: {((np.sum(change_matrix) - np.sum(np.diag(change_matrix))) / total_pixels * 100):.2f}%")
    
    # Print detailed changes
    class_names = ['Water', 'Vegetation', 'Built-up', 'Barren']
    print("\nDetailed Changes:")
    for i in range(len(class_names)):
        for j in range(len(class_names)):
            if i != j:  # Only show changes between different classes
                print(f"{class_names[i]} to {class_names[j]}: {change_matrix[i, j]:,} pixels")

if __name__ == "__main__":
    main() 