import rasterio
import numpy as np
import matplotlib.pyplot as plt
import folium
from folium import plugins
import branca.colormap as cm
import os

def plot_classification_map(classified_path, output_path, title="Land Cover Classification"):
    """
    Create a static map of the classification results.
    
    Args:
        classified_path (str): Path to classified GeoTIFF
        output_path (str): Path to save the map
        title (str): Map title
    """
    with rasterio.open(classified_path) as src:
        classified = src.read(1)
        bounds = src.bounds
    
    # Define colors for each class
    colors = {
        1: '#0000FF',  # Water - Blue
        2: '#00FF00',  # Vegetation - Green
        3: '#FF0000',  # Built-up - Red
        4: '#FFFF00'   # Barren - Yellow
    }
    
    # Create colormap
    cmap = plt.cm.colors.ListedColormap(list(colors.values()))
    
    # Create figure
    plt.figure(figsize=(12, 8))
    plt.imshow(classified, cmap=cmap)
    plt.colorbar(label='Land Cover Class')
    plt.title(title)
    
    # Add legend
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, facecolor=color, label=label)
        for label, color in zip(
            ['Water', 'Vegetation', 'Built-up', 'Barren'],
            colors.values()
        )
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Static map saved to {output_path}")

def create_interactive_map(classified_path, output_path):
    """
    Create an interactive map using Folium.
    
    Args:
        classified_path (str): Path to classified GeoTIFF
        output_path (str): Path to save the HTML map
    """
    with rasterio.open(classified_path) as src:
        classified = src.read(1)
        bounds = src.bounds
    
    # Create colormap
    colors = {
        1: '#0000FF',  # Water
        2: '#00FF00',  # Vegetation
        3: '#FF0000',  # Built-up
        4: '#FFFF00'   # Barren
    }
    
    # Create Folium map centered on Abu Dhabi
    m = folium.Map(location=[24.45, 54.37], zoom_start=10)
    
    # Add classified image
    folium.raster_layers.ImageOverlay(
        classified,
        bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
        colormap=lambda x: colors.get(x, '#000000'),
        opacity=0.7
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; 
                border:2px solid grey; z-index:9999; 
                background-color:white;
                padding:10px;
                font-size:14px;
                ">
    <p><strong>Land Cover Classes</strong></p>
    '''
    for label, color in colors.items():
        legend_html += f'<p><span style="color:{color};">■</span> {label}</p>'
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save map
    m.save(output_path)
    print(f"Interactive map saved to {output_path}")

def plot_feature_importance(importance_dict, output_path):
    """
    Create a bar plot of feature importance.
    
    Args:
        importance_dict (dict): Dictionary of feature importance scores
        output_path (str): Path to save the plot
    """
    features = list(importance_dict.keys())
    scores = list(importance_dict.values())
    
    plt.figure(figsize=(10, 6))
    plt.bar(features, scores)
    plt.title('Feature Importance')
    plt.xlabel('Features')
    plt.ylabel('Importance Score')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Feature importance plot saved to {output_path}")

def plot_change_detection(classified_2017, classified_2023, output_path):
    """
    Create a change detection map between two classified images.
    
    Args:
        classified_2017 (str): Path to 2017 classification
        classified_2023 (str): Path to 2023 classification
        output_path (str): Path to save the change map
    """
    with rasterio.open(classified_2017) as src:
        class_2017 = src.read(1)
    
    with rasterio.open(classified_2023) as src:
        class_2023 = src.read(1)
    
    # Calculate change
    change = np.zeros_like(class_2017)
    change[class_2017 != class_2023] = 1  # 1 indicates change
    
    # Create figure
    plt.figure(figsize=(12, 8))
    plt.imshow(change, cmap='hot')
    plt.colorbar(label='Change Detection')
    plt.title('Urban Change Detection (2017-2023)')
    
    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Change detection map saved to {output_path}")

def main():
    # Example usage
    data_dir = "../data"
    classified_file = os.path.join(data_dir, "sentinel2_abudhabi_2023_classified.tif")
    classified_2017 = os.path.join(data_dir, "sentinel2_abudhabi_2017_classified.tif")
    classified_2023 = os.path.join(data_dir, "sentinel2_abudhabi_2023_classified.tif")
    
    # Create output directory for visualizations
    vis_dir = os.path.join(data_dir, "visualizations")
    os.makedirs(vis_dir, exist_ok=True)
    
    # Generate static classification map
    static_map_path = os.path.join(vis_dir, "classification_map.png")
    plot_classification_map(classified_file, static_map_path)
    
    # Generate interactive map
    interactive_map_path = os.path.join(vis_dir, "interactive_map.html")
    create_interactive_map(classified_file, interactive_map_path)
    
    # Generate feature importance plot
    importance = {
        'NDVI': 0.4,
        'NDWI': 0.3,
        'NDBI': 0.3
    }
    importance_plot_path = os.path.join(vis_dir, "feature_importance.png")
    plot_feature_importance(importance, importance_plot_path)
    
    # Generate change detection map
    if os.path.exists(classified_2017) and os.path.exists(classified_2023):
        change_map_path = os.path.join(vis_dir, "change_detection.png")
        plot_change_detection(classified_2017, classified_2023, change_map_path)

if __name__ == "__main__":
    main() 