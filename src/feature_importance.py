import numpy as np
import matplotlib.pyplot as plt
import rasterio
from sklearn.ensemble import RandomForestClassifier
import os

def analyze_feature_importance(sentinel_path, landcover_path, output_dir):
    """Analyze and visualize feature importance from the Random Forest classifier."""
    # Load data
    with rasterio.open(sentinel_path) as src:
        sentinel = src.read()
        band_names = src.descriptions
    
    with rasterio.open(landcover_path) as src:
        landcover = src.read(
            out_shape=(
                src.count,
                sentinel.shape[1],
                sentinel.shape[2]
            ),
            resampling=rasterio.warp.Resampling.nearest
        )
    
    # Prepare data
    n_samples = sentinel.shape[1] * sentinel.shape[2]
    X = sentinel.reshape(sentinel.shape[0], n_samples).T
    y = landcover.reshape(n_samples)
    
    # Remove background pixels
    mask = y != 0
    X = X[mask]
    y = y[mask]
    
    # Train classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    
    # Get feature importance
    importances = clf.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    # Plot feature importance
    plt.figure(figsize=(10, 6))
    plt.title('Feature Importance in Land Cover Classification')
    plt.bar(range(len(importances)), importances[indices])
    plt.xticks(range(len(importances)), [band_names[i] for i in indices], rotation=45, ha='right')
    plt.xlabel('Spectral Bands')
    plt.ylabel('Importance Score')
    plt.tight_layout()
    
    # Save plot
    output_path = os.path.join(output_dir, 'feature_importance.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Feature importance plot saved to {output_path}")
    
    # Print feature importance scores
    print("\nFeature Importance Scores:")
    for i in indices:
        print(f"{band_names[i]}: {importances[i]:.4f}")

def main():
    data_dir = "data"
    sentinel_file = os.path.join(data_dir, "sentinel2_abudhabi_2023.tif")
    landcover_file = os.path.join(data_dir, "abudhabi_landcover.tif")
    
    if not os.path.exists(sentinel_file) or not os.path.exists(landcover_file):
        print("Error: Required input files not found")
        return
    
    analyze_feature_importance(sentinel_file, landcover_file, data_dir)

if __name__ == "__main__":
    main() 