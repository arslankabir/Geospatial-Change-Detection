# Geospatial Change Detection Project

## Overview
This project implements change detection in Abu Dhabi using Sentinel-2 imagery to analyze environmental and urban changes between 2018 and 2023. The project focuses on calculating and visualizing changes in vegetation (NDVI), water bodies (NDWI), and built-up areas (NDBI).

## Features
- **Multi-temporal Analysis**: Compare changes between 2018 and 2023
- **Spectral Indices**:
  - NDVI (Normalized Difference Vegetation Index)
  - NDWI (Normalized Difference Water Index)
  - NDBI (Normalized Difference Built-up Index)
- **Change Detection**: Calculate and visualize changes in each index
- **Area Statistics**: Calculate area of significant changes
- **Visualization**: Generate side-by-side comparisons with colorbars and legends

## Project Structure
```
├── data/                      # Data directory
│   ├── sentinel_2018.tif      # 2018 Sentinel-2 image
│   ├── sentinel_2023.tif      # 2023 Sentinel-2 image
│   ├── ndvi_changes.png       # NDVI change visualization
│   ├── ndwi_changes.png       # NDWI change visualization
│   └── ndbi_changes.png       # NDBI change visualization
├── src/                       # Source code
│   ├── download_sentinel.py   # Google Earth Engine data download
│   └── change_detection.py    # Change detection implementation
├── requirements.txt           # Project dependencies
└── README.md                 # Project documentation
```

## Setup and Installation

1. **Clone the repository**
```bash
git clone [repository-url]
cd Data-Classification-resampling
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Google Earth Engine Setup**
- Install Google Earth Engine Python API
- Authenticate with your Google account
- Set up Google Drive for data export

4. **Download Sentinel-2 Data**
```bash
python src/download_sentinel.py
```

5. **Run Change Detection**
```bash
python src/change_detection.py
```

## Implementation Details

### Data Acquisition
- Uses Google Earth Engine Python API
- Downloads Sentinel-2 imagery for 2018 and 2023
- Implements cloud masking (40% threshold)
- Exports data to Google Drive

### Spectral Indices
- **NDVI**: (NIR - Red) / (NIR + Red)
- **NDWI**: (Green - NIR) / (Green + NIR)
- **NDBI**: (SWIR - NIR) / (SWIR + NIR)

### Change Detection
- Calculates indices for both years
- Computes differences
- Generates visualizations with:
  - Side-by-side comparisons
  - Change maps
  - Colorbars and legends
- Calculates area statistics for significant changes

## Dependencies
- Python 3.x
- Google Earth Engine Python API
- Rasterio
- NumPy
- Matplotlib
- GDAL

## Future Enhancements
1. **Technical Improvements**
   - Machine learning integration
   - SAR data incorporation
   - Real-time monitoring

2. **Visualization**
   - Interactive dashboards
   - 3D visualization
   - Time-series analysis

3. **Processing**
   - Advanced cloud masking
   - Automated quality checks
   - Batch processing capabilities

## Applications
1. **Urban Planning**
   - Monitor urban expansion
   - Track infrastructure development
   - Assess environmental impact

2. **Environmental Monitoring**
   - Vegetation health tracking
   - Water body changes
   - Land use changes

3. **Disaster Management**
   - Flood monitoring
   - Drought assessment
   - Urban heat island analysis

## Contributing
Feel free to submit issues and enhancement requests!

## License
[Your chosen license] 