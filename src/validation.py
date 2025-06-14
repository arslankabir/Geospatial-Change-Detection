import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import rasterio
import os

def calculate_metrics(y_true, y_pred, class_names):
    """Calculate classification metrics."""
    # Calculate confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    # Calculate classification report
    report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
    
    return cm, report

def plot_confusion_matrix(cm, class_names, output_path):
    """Plot confusion matrix as a heatmap."""
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=class_names,
                yticklabels=class_names)
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def plot_metrics(report, output_path):
    """Plot classification metrics."""
    # Extract metrics for each class
    classes = list(report.keys())[:-3]  # Exclude 'accuracy', 'macro avg', 'weighted avg'
    precision = [report[cls]['precision'] for cls in classes]
    recall = [report[cls]['recall'] for cls in classes]
    f1_score = [report[cls]['f1-score'] for cls in classes]
    
    # Create bar plot
    x = np.arange(len(classes))
    width = 0.25
    
    plt.figure(figsize=(12, 6))
    plt.bar(x - width, precision, width, label='Precision')
    plt.bar(x, recall, width, label='Recall')
    plt.bar(x + width, f1_score, width, label='F1-Score')
    
    plt.xlabel('Land Cover Class')
    plt.ylabel('Score')
    plt.title('Classification Metrics by Class')
    plt.xticks(x, classes, rotation=45)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def validate_classification(prediction_path, ground_truth_path, output_dir):
    """Validate classification results against ground truth."""
    # Load prediction and ground truth
    with rasterio.open(prediction_path) as src:
        prediction = src.read(1)
    with rasterio.open(ground_truth_path) as src:
        ground_truth = src.read(1)
    
    # Flatten arrays
    y_pred = prediction.flatten()
    y_true = ground_truth.flatten()
    
    # Remove background pixels
    mask = y_true != 0
    y_pred = y_pred[mask]
    y_true = y_true[mask]
    
    # Define class names
    class_names = ['Water', 'Vegetation', 'Built-up', 'Barren']
    
    # Calculate metrics
    cm, report = calculate_metrics(y_true, y_pred, class_names)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Plot confusion matrix
    plot_confusion_matrix(cm, class_names, 
                         os.path.join(output_dir, 'confusion_matrix.png'))
    
    # Plot metrics
    plot_metrics(report, os.path.join(output_dir, 'classification_metrics.png'))
    
    # Print overall accuracy
    print(f"\nOverall Accuracy: {report['accuracy']:.3f}")
    
    # Print per-class metrics
    print("\nPer-class Metrics:")
    for cls in class_names:
        print(f"\n{cls}:")
        print(f"Precision: {report[cls]['precision']:.3f}")
        print(f"Recall: {report[cls]['recall']:.3f}")
        print(f"F1-Score: {report[cls]['f1-score']:.3f}")

def main():
    data_dir = "data"
    prediction_file = os.path.join(data_dir, "classification_result_2023.tif")
    ground_truth_file = os.path.join(data_dir, "abudhabi_landcover.tif")
    
    if not os.path.exists(prediction_file) or not os.path.exists(ground_truth_file):
        print("Error: Required files not found")
        return
    
    validate_classification(prediction_file, ground_truth_file, data_dir)

if __name__ == "__main__":
    main() 