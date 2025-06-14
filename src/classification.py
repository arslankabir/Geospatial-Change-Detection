import rasterio
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

class LandCoverClassifier:
    def __init__(self, n_estimators=100, random_state=42):
        """
        Initialize the land cover classifier.
        
        Args:
            n_estimators (int): Number of trees in the random forest
            random_state (int): Random seed for reproducibility
        """
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1
        )
        self.feature_names = ['NDVI', 'NDWI', 'NDBI']
        self.class_names = ['Water', 'Vegetation', 'Built-up', 'Barren']
    
    def prepare_training_data(self, features_path, labels_path):
        """
        Prepare training data from features and labels.
        
        Args:
            features_path (str): Path to features GeoTIFF
            labels_path (str): Path to labels GeoTIFF
        
        Returns:
            tuple: (X_train, X_test, y_train, y_test)
        """
        # Read features
        with rasterio.open(features_path) as src:
            features = src.read()
            features = np.moveaxis(features, 0, -1)  # Change to (height, width, bands)
        
        # Read labels
        with rasterio.open(labels_path) as src:
            labels = src.read(1)
        
        # Reshape for sklearn
        X = features.reshape(-1, features.shape[-1])
        y = labels.reshape(-1)
        
        # Remove background pixels (assuming 0 is background)
        mask = y != 0
        X = X[mask]
        y = y[mask]
        
        # Split data
        return train_test_split(X, y, test_size=0.2, random_state=42)
    
    def train(self, X_train, y_train):
        """
        Train the classifier.
        
        Args:
            X_train (numpy.ndarray): Training features
            y_train (numpy.ndarray): Training labels
        """
        self.model.fit(X_train, y_train)
        print("Model training completed.")
    
    def predict(self, features_path, output_path):
        """
        Predict land cover classes for an image.
        
        Args:
            features_path (str): Path to features GeoTIFF
            output_path (str): Path to save classification result
        """
        # Read features
        with rasterio.open(features_path) as src:
            features = src.read()
            meta = src.meta.copy()
            features = np.moveaxis(features, 0, -1)
        
        # Reshape for prediction
        X = features.reshape(-1, features.shape[-1])
        
        # Predict
        predictions = self.model.predict(X)
        
        # Reshape back to image
        predictions = predictions.reshape(features.shape[:2])
        
        # Update metadata
        meta.update({
            'count': 1,
            'dtype': 'uint8'
        })
        
        # Save predictions
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(predictions.astype('uint8'), 1)
        
        print(f"Predictions saved to {output_path}")
        return predictions
    
    def get_feature_importance(self):
        """
        Get feature importance scores.
        
        Returns:
            dict: Feature importance scores
        """
        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))
    
    def save_model(self, model_path):
        """
        Save the trained model.
        
        Args:
            model_path (str): Path to save the model
        """
        joblib.dump(self.model, model_path)
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path):
        """
        Load a trained model.
        
        Args:
            model_path (str): Path to the saved model
        """
        self.model = joblib.load(model_path)
        print(f"Model loaded from {model_path}")

def main():
    # Example usage
    data_dir = "../data"
    features_file = os.path.join(data_dir, "sentinel2_abudhabi_2023_features.tif")
    labels_file = os.path.join(data_dir, "sentinel2_abudhabi_2023_labels.tif")
    output_file = os.path.join(data_dir, "sentinel2_abudhabi_2023_classified.tif")
    model_file = os.path.join(data_dir, "land_cover_classifier.joblib")
    
    # Initialize classifier
    classifier = LandCoverClassifier()
    
    if os.path.exists(features_file) and os.path.exists(labels_file):
        # Prepare data
        X_train, X_test, y_train, y_test = classifier.prepare_training_data(
            features_file, labels_file
        )
        
        # Train model
        classifier.train(X_train, y_train)
        
        # Save model
        classifier.save_model(model_file)
        
        # Get feature importance
        importance = classifier.get_feature_importance()
        print("\nFeature Importance:")
        for feature, score in importance.items():
            print(f"{feature}: {score:.4f}")
        
        # Make predictions
        predictions = classifier.predict(features_file, output_file)
        print("\nClassification completed successfully.")
    else:
        print("Required input files not found.")

if __name__ == "__main__":
    main() 