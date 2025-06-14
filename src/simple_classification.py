import rasterio
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import os
from rasterio.warp import Resampling

def load_and_prepare_data(sentinel_path, landcover_path):
    """Load and prepare data for classification."""
    # Load Sentinel-2 data
    with rasterio.open(sentinel_path) as src:
        sentinel = src.read()
        meta = src.meta
        sentinel_transform = src.transform
        sentinel_shape = src.shape
    
    # Load land cover data and resample to match Sentinel-2
    with rasterio.open(landcover_path) as src:
        landcover = src.read(
            out_shape=(
                src.count,
                sentinel_shape[0],
                sentinel_shape[1]
            ),
            resampling=Resampling.nearest
        )
    
    # Reshape data for sklearn
    n_samples = sentinel.shape[1] * sentinel.shape[2]
    X = sentinel.reshape(sentinel.shape[0], n_samples).T
    y = landcover.reshape(n_samples)
    
    # Remove background pixels (assuming 0 is background)
    mask = y != 0
    X = X[mask]
    y = y[mask]
    
    return X, y, meta

def train_classifier(X, y):
    """Train a Random Forest classifier."""
    # Split data
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train classifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # Print accuracy
    print(f"Training accuracy: {clf.score(X_train, y_train):.3f}")
    print(f"Testing accuracy: {clf.score(X_test, y_test):.3f}")
    
    return clf

def classify_image(clf, sentinel_path, output_path):
    """Classify the entire image."""
    # Load Sentinel-2 data
    with rasterio.open(sentinel_path) as src:
        sentinel = src.read()
        meta = src.meta
    
    # Reshape for prediction
    n_samples = sentinel.shape[1] * sentinel.shape[2]
    X = sentinel.reshape(sentinel.shape[0], n_samples).T
    
    # Predict
    predictions = clf.predict(X)
    
    # Reshape back to image
    predictions = predictions.reshape(sentinel.shape[1:])
    
    # Save predictions
    meta.update({
        'count': 1,
        'dtype': 'uint8'
    })
    
    with rasterio.open(output_path, 'w', **meta) as dst:
        dst.write(predictions.astype('uint8'), 1)
    
    print(f"Classification saved to {output_path}")
    return predictions

def plot_classification(predictions, output_path):
    """Plot the classification results with proper class labels."""
    # Define class names and colors
    class_names = {
        1: 'Water',
        2: 'Vegetation',
        3: 'Built-up',
        4: 'Barren'
    }
    
    # Create a custom colormap
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728']  # Blue, Green, Orange, Red
    cmap = plt.cm.colors.ListedColormap(colors)
    
    plt.figure(figsize=(12, 10))
    
    # Plot the classification
    im = plt.imshow(predictions, cmap=cmap)
    
    # Add colorbar with class names
    cbar = plt.colorbar(im, ticks=[1, 2, 3, 4])
    cbar.set_ticklabels([class_names[i] for i in range(1, 5)])
    cbar.set_label('Land Cover Class')
    
    plt.title('Land Cover Classification - Abu Dhabi 2023', fontsize=14, pad=20)
    
    # Add a text box with accuracy information
    plt.figtext(0.02, 0.02, 
                f'Classification Results\n'
                f'Training Accuracy: {clf.score(X_train, y_train):.3f}\n'
                f'Testing Accuracy: {clf.score(X_test, y_test):.3f}',
                bbox=dict(facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Plot saved to {output_path}")

def main():
    # File paths
    data_dir = "data"
    years = [2017, 2023]
    
    for year in years:
        print(f"\nProcessing {year} data...")
        sentinel_file = os.path.join(data_dir, f"sentinel2_abudhabi_{year}.tif")
        landcover_file = os.path.join(data_dir, "abudhabi_landcover.tif")
        output_file = os.path.join(data_dir, f"classification_result_{year}.tif")
        plot_file = os.path.join(data_dir, f"classification_plot_{year}.png")
        
        # Check if files exist
        if not os.path.exists(sentinel_file):
            print(f"Error: {sentinel_file} not found")
            continue
        if not os.path.exists(landcover_file):
            print(f"Error: {landcover_file} not found")
            continue
        
        # Load and prepare data
        print("Loading and preparing data...")
        X, y, meta = load_and_prepare_data(sentinel_file, landcover_file)
        
        # Train classifier
        print("\nTraining classifier...")
        clf = train_classifier(X, y)
        
        # Classify image
        print("\nClassifying image...")
        predictions = classify_image(clf, sentinel_file, output_file)
        
        # Plot results
        print("\nPlotting results...")
        plot_classification(predictions, plot_file)
        
        # Print class distribution
        unique, counts = np.unique(predictions, return_counts=True)
        total_pixels = np.sum(counts)
        print(f"\nClass Distribution for {year}:")
        for class_id, count in zip(unique, counts):
            if class_id != 0:  # Skip background
                percentage = (count / total_pixels) * 100
                print(f"Class {class_id}: {count} pixels ({percentage:.2f}%)")
    
    print("\nDone! All years processed.")

if __name__ == "__main__":
    main() 